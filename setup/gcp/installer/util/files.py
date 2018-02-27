# Copyright 2017 The Forseti Security Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" File utility functions."""

from __future__ import print_function
import os

import ruamel.yaml

import constants
import utils


def generate_deployment_templates(template_type, values, datetimestamp):
    """Generate deployment templates.

    Args:
        template_type (str): Type of the template, either cli or server
        values (dict): Values needed for deployment
        datetimestamp (str): Timestamp

    Returns:
        str: Path of the deployment template

    Raises:
        KeyError: KeyError
    """

    template_type = template_type.lower()

    if template_type not in constants.INPUT_DEPLOYMENT_TEMPLATE_FILENAME:
        raise KeyError # template type not found

    input_template_filename = (
        constants.INPUT_DEPLOYMENT_TEMPLATE_FILENAME[template_type])

    # Deployment template in file
    deploy_tpl_path = os.path.abspath(
        os.path.join(
            constants.ROOT_DIR_PATH,
            'deployment-templates',
            input_template_filename))

    out_tpl_path = os.path.abspath(
        os.path.join(
            constants.ROOT_DIR_PATH,
            'deployment-templates',
            'deploy-forseti-{}-{}.yaml'.format(template_type, datetimestamp)))

    if generate_file_from_template(deploy_tpl_path,
                                   out_tpl_path,
                                   values):
        return out_tpl_path

    # Deployment template not generated successfully
    return None


def generate_forseti_conf(template_type, vals, datetimestamp):
    """Generate Forseti conf file.

    Args:
        template_type (str): Type of the template, either cli or server
        vals (dict): Values needed for deployment
        datetimestamp (str): Timestamp

    Returns:
        str: Path of the deployment template

    Raises:
        KeyError: KeyError
    """

    template_type = template_type.lower()

    if template_type not in constants.INPUT_CONFIGURATION_TEMPLATE_FILENAME:
        raise KeyError # template type not found

    input_template_name = (
        constants.INPUT_CONFIGURATION_TEMPLATE_FILENAME[template_type])

    forseti_conf_in = os.path.abspath(
        os.path.join(
            constants.ROOT_DIR_PATH,
            'configs', template_type, input_template_name))
    forseti_conf_gen = os.path.abspath(
        os.path.join(
            constants.ROOT_DIR_PATH, 'configs', template_type,
            'forseti_conf_{}_{}.yaml'.format(template_type, datetimestamp)))

    conf_values = utils.sanitize_conf_values(vals)

    if generate_file_from_template(forseti_conf_in,
                                   forseti_conf_gen,
                                   conf_values):
        return forseti_conf_gen

    # forseti_conf not generated successfully
    return None


def update_rule_files(values, rule_dir_path):
    """Update rule files default values.

    Args:
        rule_dir_path (str): Rule directory path.
        values (dict): Values needed for deployment

    Raises:
        KeyError: KeyError
    """

    files_and_dirs = os.listdir(rule_dir_path)

    full_paths = [os.path.join(rule_dir_path, f) for f in files_and_dirs]

    file_paths = [path for path in full_paths if os.path.isfile(path)]

    for file_path in file_paths:
        generate_file_from_template(file_path, file_path, values)


def generate_file_from_template(template_path, output_path, template_values):
    """Write to file.

    Args:
        template_path (str): Input template path
        output_path (str): Path of the output file
        template_values (dict): Values to replace the
                                ones in the input template
    Returns:
        bool: Whether or not file has been generated
    """

    try:
        with open(template_path, 'r') as in_tmpl:
            tmpl_contents = in_tmpl.read()
            out_contents = tmpl_contents.format(**template_values)
        with open(output_path, 'w') as out_file:
            out_file.write(out_contents)
            return True
    except EnvironmentError:
        pass
    return False


def copy_file_to_destination(file_path, output_path,
                             is_directory=False, dry_run=False):
    """Copy the config to the created bucket.

    Args:
        file_path (str): Path to the file
        output_path (str): Path of the copied file
        is_directory (bool): Whether or not the input file_path is a directory
        dry_run (bool): Whether or not the installer is in dry run mode

    Returns:
        bool: True if copy file succeeded, otherwise False.
    """

    if dry_run:
        return False

    if is_directory:
        args = ['gsutil', 'cp', '-r', file_path, output_path]
    else:
        args = ['gsutil', 'cp', file_path, output_path]

    return_code, _, _ = utils.run_command(args)
    if return_code:
        return False
    return True


def read_yaml_file_from_local(file_path):
    """Load file from local path.

    Args:
      file_path (str): The path to the file.

    Returns:
        dict: The parsed dict from the loaded file.
    """

    def _parse_yaml(data):
        """Parse yaml data.

        Args:
            data (stream): A yaml data stream to parse.

        Returns:
            dict: The stream successfully parsed into a dict.

        Raises:
            YAMLError: If there was an error parsing the stream.
        """
        try:
            return ruamel.yaml.load(data, Loader=ruamel.yaml.RoundTripLoader)
        except ruamel.yaml.YAMLError as yaml_error:
            raise yaml_error

    with open(os.path.abspath(file_path), 'r') as f:
        return _parse_yaml(f)


def write_data_to_yaml_file(data, output_file_path):
    """Write data to yaml file.

    Args:
        data (dict): A yaml data stream to parse.
        output_file_path (str): Output file path.
    """

    with open(output_file_path, 'w') as outfile:
        ruamel.yaml.dump(data, outfile,
                         Dumper=ruamel.yaml.RoundTripDumper,
                         indent=4)
