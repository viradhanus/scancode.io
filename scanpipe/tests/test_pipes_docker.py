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

import json
import tempfile
from pathlib import Path

from django.apps import apps
from django.test import TestCase

from scanpipe.models import CodebaseResource
from scanpipe.models import Project
from scanpipe.pipes import docker

scanpipe_app = apps.get_app_config("scanpipe")


class ScanPipeDockerPipesTest(TestCase):
    data_path = Path(__file__).parent / "data"

    def assertResultsEqual(self, expected_file, results, regen=False):
        """
        Set `regen` to True to regenerate the expected results.
        """
        if regen:
            expected_file.write_text(results)

        expected_data = expected_file.read_text()
        self.assertEqual(expected_data, results)

    def test_pipes_docker_get_image_data_contains_layers_with_relative_paths(self):
        extract_target = str(Path(tempfile.mkdtemp()) / "tempdir")
        input_tarball = str(self.data_path / "docker-images.tar.gz")

        # Extract the image first
        images, errors = docker.extract_image_from_tarball(
            input_tarball,
            extract_target,
            verify=False,
        )
        self.assertEqual([], errors)

        images_data = [docker.get_image_data(i) for i in images]
        results = json.dumps(images_data, indent=2)
        expected_location = self.data_path / "docker-images.tar.gz-expected-data-1.json"
        self.assertResultsEqual(expected_location, results, regen=False)

        # Extract the layers second
        errors = docker.extract_layers_from_images_to_base_path(
            base_path=extract_target,
            images=images,
        )
        self.assertEqual([], errors)

        images_data = [docker.get_image_data(i) for i in images]
        results = json.dumps(images_data, indent=2)
        expected_location = self.data_path / "docker-images.tar.gz-expected-data-2.json"
        self.assertResultsEqual(expected_location, results, regen=False)

    def test_pipes_docker_tag_whiteout_codebase_resources(self):
        p1 = Project.objects.create(name="Analysis")
        resource1 = CodebaseResource.objects.create(project=p1, path="filename.ext")
        resource2 = CodebaseResource.objects.create(project=p1, name=".wh.filename2")

        docker.tag_whiteout_codebase_resources(p1)
        resource1.refresh_from_db()
        resource2.refresh_from_db()
        self.assertEqual("", resource1.status)
        self.assertEqual("ignored-whiteout", resource2.status)
