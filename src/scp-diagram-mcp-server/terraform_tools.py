# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

"""SCP Terraform provider documentation lookup for the scp-diagram-mcp-server.

Provides read-only access to the resource and data-source reference docs of the
`terraform-provider-samsungcloudplatformv2` provider, mirrored locally under
`terraform_docs/`. Each doc file contains both example HCL usage and the full
attribute schema for one resource/data-source type.
"""

import os
import re
from models import (
    TerraformExampleResponse,
    TerraformResourceCategory,
    TerraformResourceListResponse,
)
from typing import List, Optional


TERRAFORM_DOCS_DIR = os.path.join(os.path.dirname(__file__), 'terraform_docs')
RESOURCES_DIR = os.path.join(TERRAFORM_DOCS_DIR, 'resources')
DATA_SOURCES_DIR = os.path.join(TERRAFORM_DOCS_DIR, 'data-sources')

# Terraform resource/data-source type names only ever contain lowercase
# letters, digits and underscores.
VALID_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')

PROVIDER_PREFIX = 'samsungcloudplatformv2_'
PROVIDER_DOC_PATH = os.path.join(TERRAFORM_DOCS_DIR, 'index.md')
PROVIDER_DOC_NAMES = {'provider', 'index'}


def _list_names(directory: str, name_filter: Optional[str] = None) -> List[str]:
    """List the resource/data-source type names available in a docs directory."""
    if not os.path.isdir(directory):
        return []

    names = [f[:-3] for f in os.listdir(directory) if f.endswith('.md')]
    if name_filter:
        names = [n for n in names if name_filter.lower() in n.lower()]
    return sorted(names)


def list_terraform_resources(
    name_filter: Optional[str] = None,
) -> TerraformResourceListResponse:
    """List available SCP Terraform resource and data-source types.

    Args:
        name_filter: Optional case-insensitive substring filter (e.g. "virtualserver").

    Returns:
        TerraformResourceListResponse: Matching resource and data-source type names.
    """
    return TerraformResourceListResponse(
        resources=_list_names(RESOURCES_DIR, name_filter),
        data_sources=_list_names(DATA_SOURCES_DIR, name_filter),
        filtered=name_filter is not None,
        filter_info={'name_filter': name_filter} if name_filter else None,
    )


def get_terraform_examples(
    resource_names: str,
    category: TerraformResourceCategory = TerraformResourceCategory.ALL,
) -> TerraformExampleResponse:
    """Get SCP Terraform reference docs (example HCL + attribute schema) for resource types.

    Args:
        resource_names: Comma-separated resource/data-source type names, with or without
            the `samsungcloudplatformv2_` prefix (e.g. "virtualserver_server,vpc_vpc").
            Pass "provider" to get the provider configuration doc instead (required_providers
            block, authentication via SCP_TF_* env vars or ~/.scpconf/).
        category: Limit the lookup to 'resource', 'data-source', or 'all' (default).

    Returns:
        TerraformExampleResponse: Doc content keyed by "<name> (resource|data-source)",
        plus a list of names that had no matching doc.
    """
    examples = {}
    not_found = []

    for raw_name in resource_names.split(','):
        name = raw_name.strip()
        if not name:
            continue

        cleaned = name
        if cleaned.startswith(PROVIDER_PREFIX):
            cleaned = cleaned[len(PROVIDER_PREFIX) :]

        if cleaned.lower() in PROVIDER_DOC_NAMES:
            if os.path.isfile(PROVIDER_DOC_PATH):
                with open(PROVIDER_DOC_PATH, 'r') as f:
                    examples['provider (configuration)'] = f.read()
            else:
                not_found.append(name)
            continue

        if not VALID_NAME_PATTERN.match(cleaned):
            not_found.append(name)
            continue

        found = False

        if category in (TerraformResourceCategory.RESOURCE, TerraformResourceCategory.ALL):
            path = os.path.join(RESOURCES_DIR, f'{cleaned}.md')
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    examples[f'{cleaned} (resource)'] = f.read()
                found = True

        if category in (TerraformResourceCategory.DATA_SOURCE, TerraformResourceCategory.ALL):
            path = os.path.join(DATA_SOURCES_DIR, f'{cleaned}.md')
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    examples[f'{cleaned} (data-source)'] = f.read()
                found = True

        if not found:
            not_found.append(name)

    return TerraformExampleResponse(examples=examples, not_found=not_found)
