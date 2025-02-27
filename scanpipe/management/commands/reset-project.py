# SPDX-License-Identifier: Apache-2.0
#
# http://nexb.com and https://github.com/nexB/scancode.io
# The ScanCode.io software is licensed under the Apache License version 2.0.
# Data generated with ScanCode.io is provided as-is without warranties.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# Data Generated with ScanCode.io is provided on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. No content created from
# ScanCode.io should be considered or used as legal advice. Consult an Attorney
# for any legal advice.
#
# ScanCode.io is a free software code scanning tool from nexB Inc. and others.
# Visit https://github.com/nexB/scancode.io for support and download.

import sys

from scanpipe.management.commands import ProjectCommand


class Command(ProjectCommand):
    help = (
        "Resets a project removing all database entrie and all data on disks "
        "except for the input/ directory."
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Do not prompt the user for input of any kind.",
        )

    def handle(self, *inputs, **options):
        super().handle(*inputs, **options)

        if options["interactive"]:
            confirm = input(
                f"You have requested the reset of the {self.project} project.\n"
                f"This will IRREVERSIBLY DESTROY all data, except inputs, related to "
                f"that project. \n"
                f"Are you sure you want to do this?\n"
                f"Type 'yes' to continue, or 'no' to cancel: "
            )
            if confirm != "yes":
                self.stdout.write("Reset cancelled.")
                sys.exit(0)

        self.project.reset(keep_input=True)

        msg = (
            f"All data, except inputs, for the {self.project} project have been "
            f"removed."
        )
        self.stdout.write(self.style.SUCCESS(msg))
