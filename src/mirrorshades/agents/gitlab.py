# Copyright (c) 2020-2021 Paul Barker <paul@pbarker.dev>
# SPDX-License-Identifier: Apache-2.0

import sys
from dataclasses import dataclass, field
from typing import List
from urllib.parse import urlparse

from .base import Agent
from .git import Git


class Gitlab(Agent):
    @dataclass
    class Properties:
        name: str
        private_token: str
        server: str = "https://gitlab.com"
        groups: List[str] = field(default_factory=list)
        projects: List[str] = field(default_factory=list)

    def mirror(self):
        try:
            import gitlab
        except ModuleNotFoundError:
            print(
                "The `python-gitlab` python package is needed to mirror from GitLab.",
                file=sys.stderr,
            )
            print(
                "Please install this (for example, using `pip install python-gitlab`)"
                " and try again.",
                file=sys.stderr,
            )
            sys.exit(1)

        repositories = []

        gl = gitlab.Gitlab(
            self.properties.server, private_token=self.properties.private_token
        )

        for group_path in self.properties.groups:
            group = gl.groups.get(group_path)
            for project in group.projects.list(include_subgroups=True):
                repositories.append(project.path_with_namespace)

        for project_path in self.properties.projects:
            project = gl.projects.get(project_path)
            repositories.append(project.path_with_namespace)

        url = urlparse(self.properties.server)
        location_with_auth = f"oauth2:{self.properties.private_token}@{url.netloc}"
        url_prefix = url._replace(netloc=location_with_auth).geturl()
        git_properties = {
            "name": self.properties.name,
            "url_prefix": url_prefix,
            "repositories": repositories,
        }
        git = Git(git_properties)
        git.mirror()
