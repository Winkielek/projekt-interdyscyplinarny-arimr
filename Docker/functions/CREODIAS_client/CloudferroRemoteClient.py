import datetime
import time
import os

from RemoteClient import RemoteClient


class CloudferroRemoteClient:
    """
    API for remote usage find_data.py script and downloading prepared datasets.
    """

    def __init__(
        self,
        host: str,
        ssh_key_filepath: str,
        script_dir: str = "python_scripts",
        ignore_check=False,
    ):
        self.script_dir = script_dir
        self.python_files = [
            "CloudferroAPI.py",
            "CloudferroResult.py",
            "check_dataset.py",
            "find_data.py",
            "prepare_dataset.py",
        ]
        self.shell_files = [
            "install_dependences.sh",
        ]
        self.records_downloaded = []
        self.records_to_download = 0
        self.version_file = "version"
        self.remote_client = RemoteClient(
            host=host,
            username="eouser",
            ssh_key_filepath=ssh_key_filepath,
            remote_path="/home/eouser/",
        )
        if not ignore_check:
            self._check_remote_version()
        self._clean_inactive_screens()

    def find_prepare_and_download(self, arguments: dict):
        """
        Executes find_data.py script on remote machine using passed arguments
        :param arguments: dictionary with all arguments used by find_data.py script
        :return: None
        """
        if len(arguments["diff_days"]) > 0:
            query = "sudo python3 find_data.py -s {} -l {} -r {} -c {} -p {} -e {} -i {} -n {} -z {}".format(
                arguments["satellite"],
                arguments["proc_level"],
                arguments["records"],
                arguments["cloud"],
                arguments["position"],
                arguments["end_date"],
                arguments["diff_days"],
                arguments["name"],
                arguments["resize"],
            )
        else:
            query = "sudo python3 find_data.py -s {} -l {} -r {} -c {} -p {} -t {} -e {} -n {} -z {}".format(
                arguments["satellite"],
                arguments["proc_level"],
                arguments["records"],
                arguments["cloud"],
                arguments["position"],
                arguments["start_date"],
                arguments["end_date"],
                arguments["name"],
                arguments["resize"],
            )
        # print(query)
        if self.is_active():
            resp = input(
                "Other preparation script is running. Do you want to continue with your query?[y/n] "
            )
            if resp.lower() == "n" or resp.lower() != "y":
                print("Ending")
                exit(0)

        self.records_to_download = int(arguments["records"])

        shell, stdin, stdout, stderr = self.remote_client.invoke_shell()
        shell.send("screen\r\n")
        time.sleep(1)
        shell.send("cd python_scripts\r\n")
        shell.send(query + "\r\n")
        time.sleep(1)
        if self.is_active():
            print("Preparation for query:\n{}\nstarted in screen".format(query))
            self.download_during()
        else:
            print("Preparation for query:\n{}\nFAILED to start in screen".format(query))

    def remove_data(self):
        """
        Allows removing data from server
        :return: None
        """
        response = self.remote_client.execute_command(
            "ls {}".format(self.script_dir + "/out/")
        )
        prepared_idx = []
        for itr, item in enumerate(response):
            resp = self.remote_client.execute_command(
                "ls {} | grep done".format(self.script_dir + "/out/" + item)
            )
            if len(resp) == 1:
                resp = self.remote_client.execute_command(
                    "ls {} -A".format(self.script_dir + "/out/" + item)
                )
                print(f"#{itr} {item} (elements: {len(resp) - 1})")
                prepared_idx.append(itr)

        if self.is_active():
            print("Warning. Data preparation is ongoing.")
        if len(prepared_idx) > 0:
            selected = int(input("Select number to remove: "))
            path = self.script_dir + "/out/" + response[selected]
            response = self.remote_client.execute_command("sudo rm -r {}".format(path))
        else:
            print(
                "There is no fully prepared dataset. Start data preparation using -f argument "
                "or wait if there is ongoing process"
            )

    def download_prepared(self):
        """
        Allows selection of dataset to be downloaded from prepared data
        :return: None
        """
        response = self.remote_client.execute_command(
            "ls {}".format(self.script_dir + "/out/")
        )
        prepared_idx = []
        for itr, item in enumerate(response):
            resp = self.remote_client.execute_command(
                "ls {} | grep done".format(self.script_dir + "/out/" + item)
            )
            if len(resp) == 1:
                resp = self.remote_client.execute_command(
                    "ls {} -A".format(self.script_dir + "/out/" + item)
                )
                print(f"#{itr} {item} (elements: {len(resp) - 1})")
                prepared_idx.append(itr)

        if self.is_active():
            print("Warning. Data preparation is ongoing.")
        if len(prepared_idx) > 0:
            selected = int(input("Select number to download: "))
            download_folder = str(input("Pass folder name to download to: "))
            path = self.script_dir + "/out/" + response[selected]
            self.remote_client.download_dir(
                remote_path=path, local_path=download_folder
            )
        else:
            print(
                "There is no fully prepared dataset. Start data preparation using -f argument "
                "or wait if there is ongoing process"
            )

    def download_during(self):
        response = self.remote_client.execute_command(
            "ls {} -t | head -n1".format(self.script_dir + "/out/")
        )
        out_dir = response[0]
        local_path = os.path.join("download", out_dir)
        print(f"Downloading from {out_dir} to {local_path}")

        while self.is_active():
            time.sleep(10)
            print("10s ping")
            response = self.remote_client.execute_command(
                "ls {} -Alt".format(self.script_dir + "/out/" + out_dir)
            )
            if len(response) > 2:
                tmp = response[1].split(" ")
                tmp = [x for x in tmp if x]
                last_modified = datetime.datetime.strptime(tmp[7], "%H:%M")
                for resp in response:
                    if str(resp).startswith("d"):
                        tmp = resp.split(" ")
                        tmp = [x for x in tmp if x]
                        dir_modified = datetime.datetime.strptime(tmp[7], "%H:%M")
                        if resp.find(
                            "SAFE"
                        ) > 0 and last_modified > dir_modified + datetime.timedelta(
                            0, 60
                        ):
                            record_name = tmp[-1]
                            if record_name not in self.records_downloaded:
                                path = (
                                    self.script_dir
                                    + "/out/"
                                    + out_dir
                                    + "/"
                                    + record_name
                                )
                                self.remote_client.download_dir(
                                    path, local_path, split_task=False
                                )
                                self.records_downloaded.append(record_name)

        print("Remote script ended. Downloading missing directories.")
        response = self.remote_client.execute_command(
            "ls {} -Al".format(self.script_dir + "/out/" + out_dir)
        )
        for resp in response:
            if str(resp).startswith("d"):
                record_name = resp.split(" ")[-1]
                if record_name not in self.records_downloaded:
                    path = self.script_dir + "/out/" + out_dir + "/" + record_name
                    self.remote_client.download_dir(path, local_path, split_task=False)
                    self.records_downloaded.append(record_name)

    def is_active(self):
        """
        Checks if there is active data selection task
        :return: True if there is, False otherwise
        """
        response = self.remote_client.execute_command("ps all")
        for resp in response:
            if resp.find("python3 find_data.py") >= 0:
                return True

        return False

    def _upload_scripts(self):
        """
        Helper function for script uploading
        :return: None
        """
        print("Uploading scripts")
        files = self.python_files + self.shell_files + [self.version_file]
        self.remote_client.bulk_upload(files, self.script_dir)

    @staticmethod
    def _files_list_check(local: list, remote: list):
        """
        Checks if all needed files are present in remote location
        :param local: list of local files
        :param remote: list of files on remote machine
        :return: True if ok, False otherwise
        """
        for file in local:
            if file in remote:
                remote.remove(file)
        if len(remote) >= 0:
            return True
        else:
            return False

    def _clean_inactive_screens(self):
        """
        Cleans all inactive screens on remote server
        :return: None
        """
        if not self.is_active():
            response = self.remote_client.execute_command("screen -ls")
            for resp in response:
                if resp.find("Detached") >= 0:
                    pid = resp.split(".")[0].strip()
                    tmp = self.remote_client.execute_command(
                        "screen -S {} -X quit".format(pid)
                    )
                    time.sleep(0.1)

    def _check_remote_version(self):
        """
        Checks version of scripts on the remote machine and replaces them if necessary.
        :return: None
        """
        response = self.remote_client.execute_command(f"ls")
        if self.script_dir not in response:
            print("Creating script directory")
            self.remote_client.execute_command(f"mkdir {self.script_dir}")
            self._upload_scripts()
            return
        response = self.remote_client.execute_command(f"ls {self.script_dir}")
        if len(response) == 0:
            self._upload_scripts()
        python_files = [k for k in response if ".py" in k]
        shell_files = [k for k in response if ".sh" in k]
        version_files = [k for k in response if self.version_file in k]

        scripts_ok = False
        if len(version_files) == 1:
            response = self.remote_client.execute_command(
                "cat {}".format(self.script_dir + "/" + self.version_file)
            )
            if len(response) == 1:
                version = ""
                with open(self.version_file) as fh:
                    version = fh.readline().strip("\n")
                if response[0] == version:
                    if len(self.python_files) <= len(python_files) and len(
                        self.shell_files
                    ) <= len(shell_files):
                        if self._files_list_check(
                            self.python_files, python_files
                        ) and self._files_list_check(self.shell_files, shell_files):
                            scripts_ok = True
        if not scripts_ok:
            self._upload_scripts()
        else:
            print("Remote scripts ok")
