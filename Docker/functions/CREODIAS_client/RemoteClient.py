import os

import hashlib

import paramiko
from paramiko.auth_handler import AuthenticationException

import scp
from scp import SCPException


def input_validation(input_str: str, error_str: str, input_list: list):
    while True:
        try:
            inp = input(input_str)
            if inp not in input_list:
                raise ValueError
            break
        except ValueError:
            print(error_str)
            print("Use [{}]".format("/".join(input_list)))
    return inp


class RemoteClient:
    """
    Wrapper Class for ssh and scp based on paramiko and scp packages
    """

    def __init__(
        self, host: str, username: str, ssh_key_filepath: str, remote_path: str = ""
    ):
        self.host = host
        self.username = username
        self.ssh_key_filepath = ssh_key_filepath
        self.remote_path = remote_path
        if len(remote_path):
            self.remote_path = "/home/{}".format(username)
        self.ssh_client = None
        self.scp_client = None
        self.connection = None

    def __del__(self):
        if self.ssh_client:
            self.ssh_client.close()
        if self.scp_client:
            self.scp_client.close()

    def download_file(
        self, remote_path: str, local_path: str = "", allow_overwrite: bool = False
    ):
        """
        Allows file download from remote path to local path
        :param remote_path: path to remote file
        :param local_path: path to download directory
        :param allow_overwrite: if True assumes "yes" as answer to all prompts and run non-interactively
        :return: None
        """
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        if not allow_overwrite:
            filename = os.path.split(remote_path)[1]
            filepath = os.path.join(local_path, filename)
            if os.path.exists(filepath):
                if self._check_local_and_remote_file(remote_path, local_path, filename):
                    print(
                        f"File {remote_path} exist in {local_path} and hash keys and size are equal. File omitted."
                    )
                    return
                else:
                    resp = input_validation(
                        f"File {remote_path} exist in {local_path} but there are differences. Overwrite local?[y/n]",
                        "Input not recognised.",
                        ["y", "n"],
                    )
                    if resp.lower() == "n":
                        print("File omitted.")
                        return

        self.scp_client.get(remote_path, local_path=local_path)

    def download_dir(
        self,
        remote_path: str,
        local_path: str = "",
        split_task: bool = True,
        allow_overwrite: bool = False,
    ):
        """
        Allows recursive directory download from remote path to local path
        :param remote_path: path to remote directory
        :param local_path: path to download directory
        :param split_task: if False downloads all data as one chunk, if True downloads subdirectory by subdirectory
        :param allow_overwrite: if True assumes "yes" as answer to all prompts and run non-interactively
        :return: None
        """
        self.connection = self._connect()
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        if split_task:
            response = self.execute_command("ls {} -A".format(remote_path))
            for resp in response:
                directory = resp
                tmp_remote_path = remote_path + "/" + directory
                tmp_local_path = os.path.join(local_path, remote_path.split("/")[-1])
                if not os.path.exists(tmp_local_path):
                    os.makedirs(tmp_local_path)
                else:
                    if not allow_overwrite:
                        files = self._get_files_in_remote(tmp_remote_path)
                        files_locally = []
                        for f in files:
                            filename = os.path.split(f)[1]
                            filepath = os.path.join(tmp_local_path, directory, filename)
                            if os.path.exists(filepath):
                                if self._check_local_and_remote_file(
                                    f, os.path.join(tmp_local_path, directory), filename
                                ):
                                    files_locally.append(f)
                        if len(files_locally) == 0:
                            pass
                        elif len(files) == len(files_locally):
                            print(
                                f"Data the same. Remote directory omitted: {tmp_remote_path}."
                            )
                            continue
                        else:
                            print(
                                f"Some data needs to be overwritten in {tmp_local_path}"
                            )
                            resp = input_validation(
                                f"Files from remote path exist in local but there are differences. "
                                f"Overwrite local?[y/n]",
                                "Input not recognised.",
                                ["y", "n"],
                            )
                            if resp.lower() == "n":
                                print(f"Remote directory omitted: {tmp_remote_path}")
                                continue
                print(f"Downloading directory: {tmp_remote_path} to {tmp_local_path}")
                self.scp_client.get(
                    tmp_remote_path, local_path=tmp_local_path, recursive=True
                )
        else:
            print(f"Downloading directory: {remote_path} to {local_path}")
            self.scp_client.get(remote_path, local_path=local_path, recursive=True)

    def execute_command(self, command: str, strip_new_line: bool = True):
        """
        Executes passed command in connected shell. Warning! Every command is executed in separate shell
        :param command: linux shell command
        :param strip_new_line: if True returned data is stripped from '\n'
        :return: server response
        """
        self.connection = self._connect()
        stdin, stdout, stderr = self.connection.exec_command(command)
        stdout.channel.recv_exit_status()
        response = stdout.readlines()
        if strip_new_line:
            response = [s.strip("\n") for s in response]
        return response

    def execute_commands(self, commands: list, one_shell: bool = False):
        """
        Executes passed commands in connected shell. Warning!
        Every command is executed in separate shell unless one_shell is set to True
        :param commands: list of commands to be executed
        :param one_shell: if True all commands will be executed using the same shell
        :return: None
        """
        self.connection = self._connect()
        if one_shell:
            shell, stdin, stdout, stderr = self.invoke_shell()
            for cmd in commands:
                shell.send(cmd + "\r\n")
                stdout.channel.recv_exit_status()
                response = stdout.readlines()
                print(f"INPUT: {cmd}")
                for line in response:
                    print("OUTPUT: {}".format(line.strip("\n")))
        else:
            for cmd in commands:
                stdin, stdout, stderr = self.connection.exec_command(cmd)
                stdout.channel.recv_exit_status()
                response = stdout.readlines()
                print(f"INPUT: {cmd}")
                for line in response:
                    print("OUTPUT: {}".format(line.strip("\n")))

    def get_channel(self):
        """
        Creates and returns communication channel
        :return: opened channel for ssh communication
        """
        self.connection = self._connect()

        return self.connection.get_transport().open_session()

    def invoke_shell(self):
        """
        Creates and returns communication channel as shell
        :return: opened shell with standard input, output and error streams
        """
        self.connection = self._connect()
        shell = self.connection.invoke_shell()
        stdin = shell.makefile_stdin("wb", -1)
        stdout = shell.makefile("r", -1)
        stderr = shell.makefile_stderr("r", -1)
        return shell, stdin, stdout, stderr

    def bulk_upload(self, files: list, relative_path: str = ""):
        """
        Allows uploading multiple files to one location
        :param files: list of local paths
        :param relative_path: path to remote directory
        :return: None
        """
        self.connection = self._connect()
        if len(relative_path) == 0:
            relative_path = self.remote_path
        else:
            relative_path = (
                "/" + self.remote_path.strip("/") + "/" + relative_path.strip("/")
            )
        uploads = [self._upload_single_file(file, relative_path) for file in files]
        print(
            f"Finished uploading {len(uploads)} files to {relative_path} on {self.host}"
        )

    def _connect(self):
        """
        Helper function for acquiring ssh connection and preparing clients for ssh and scp
        :return: ssh client
        """
        if self.connection is None:
            try:
                self.client = paramiko.SSHClient()
                self.client.load_system_host_keys()
                self.client.set_missing_host_key_policy(paramiko.WarningPolicy)
                self.client.connect(
                    self.host,
                    username=self.username,
                    key_filename=self.ssh_key_filepath,
                    timeout=10000,
                )
                self.scp_client = scp.SCPClient(self.client.get_transport())
            except AuthenticationException as error:
                print(f"Authentication failed. {error}")
                raise error
        return self.client

    def _check_size(
        self, local_path: str, remote_path: str, filename: str = None
    ) -> bool:
        """
        Helper function for file size comparing
        :param local_path: path to local file
        :param remote_path: path to remote file
        :return: True if same, False otherwise
        """
        if filename is None:
            filename = os.path.split(remote_path)[1]
        filepath = os.path.join(local_path, filename)
        response = self.execute_command(f"ls -Al {remote_path} | grep {filename}")
        if len(response) == 0:
            print("File not found")
            return False
        remote_size = int(response[0].split(" ")[4])
        local_size = os.path.getsize(filepath)
        if remote_size == local_size:
            return True
        else:
            return False

    def _check_hash(self, local_path: str, remote_path: str, filename: str = None):
        """
        Helper function for file hash comparing
        :param local_path: path to local file
        :param remote_path: path to remote file
        :return: True if same, False otherwise
        """
        if filename is None:
            filename = os.path.split(remote_path)[1]
        filepath = os.path.join(local_path, filename)
        response = self.execute_command(f"sha256sum -b {remote_path}")
        remote_hash = response[0].split(" ")[0]
        with open(filepath, "rb") as f:
            byts = f.read()
            local_hash = hashlib.sha256(byts).hexdigest()
        if local_hash == remote_hash:
            return True
        else:
            return False

    def _check_local_and_remote_file(
        self, remote_path: str, local_path: str, filename: str
    ) -> bool:
        if self._check_size(local_path, remote_path, filename):
            if self._check_hash(local_path, remote_path, filename):
                return True
        return False

    def _get_files_in_remote(self, remote_path: str) -> list:
        files = []
        response = self.execute_command("ls {} -RAl".format(remote_path))
        directory = str(response[0]).rstrip(":")
        nex_dir_flag = False
        for resp in response:
            if resp == "":
                nex_dir_flag = True
            elif nex_dir_flag:
                nex_dir_flag = False
                directory = str(resp).rstrip(":")
            elif str(resp).startswith("-"):
                tmp = resp.split(" ")
                tmp = [x for x in tmp if x]
                files.append(directory + "/" + tmp[8])
        return files

    def _upload_single_file(self, file, remote_path: str):
        """
        Allows uploading single file to remote server
        :param file: path to file
        :param remote_path: path to remote folder
        :return: True if successful, False otherwise
        """
        uploaded = False
        try:
            self.scp_client.put(file, recursive=True, remote_path=remote_path)
            uploaded = True
        except SCPException as error:
            print(error)
            raise error
        finally:
            print(f"Uploaded {file} to {self.remote_path}")
            return uploaded
