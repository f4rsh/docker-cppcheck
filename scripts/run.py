#!/usr/bin/python

import os
import sys
import subprocess
import platform
import re

class Runner(object):

    def __init__(self):
        self.username = os.getenv("DOCKER_USERNAME", "uilianries")
        self.password = os.getenv("DOCKER_PASSWORD", "").replace('"', '\\"')
        self.upload = os.getenv("DOCKER_UPLOAD", False)
        travis_branch = os.getenv("TRAVIS_BRANCH", "")
        appveyor_branch = os.getenv("APPVEYOR_REPO_BRANCH","")
        self.stable_branch = os.getenv("DOCKER_STABLE_BRANCH", "master")
        self.service = os.getenv("DOCKER_SERVICE", "")
        self.branch = travis_branch if travis_branch != "" else appveyor_branch
        self.compiler = "Visual Studio" if platform.system() == "Windows" else "gcc"
        version_match = re.match(r"\D+(\d+).*", self.service)
        self.compiler_version = version_match.group(1) if platform.system() == "Windows" else '.'.join(version_match.group(1))
        self.cross_building = "arm" in self.service
        self.image = "%s/%s" % (self.username, self.service)

    def build(self):
        subprocess.check_call(["docker-compose", "build", self.service])

    def deploy(self):
        if not self.upload:
            print("Skiping upload, the option is disabled.")
            sys.exit(0)

        if self.stable_branch != self.branch:
            print("Skiping upload, branch %s is not stable" % self.branch)
            sys.exit(0)

        if not self.username:
            print("Could not upload, username was not defined.")
            sys.exit(1)

        if not self.password:
            print("Could not upload, password was not defined.")
            sys.exit(1)

        subprocess.check_call(["docker", "login", "-u", self.username, "-p", self.password])
        subprocess.check_call(["docker-compose", "push", self.service])

    def run(self):
        self.build()
        self.deploy()

if __name__ == "__main__":
    runner = Runner()
    runner.run()