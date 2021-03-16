# type: ignore
# pylint: skip-file, disable-all
"""
Annotates Speeches XML files to TXT file
"""
import os
# rule annotate_speeches:
#     message:
#         "step: annotate_speeches"
#     # log: LOG_NAME
#     output:
#         filename=jj(config.parla_clarin.folder, '{basename}.xml'),
#     shell:
#         """
#         pushd \
#         && cd {sparv_folder} \
#         && sparv run \
#         && popd
#         """
