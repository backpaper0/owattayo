#!/bin/bash
set -euo pipefail

# Windowsでマウントしたディレクトリの所有者がrootになってしまう課題へ対応するスクリプト

USERNAME=${1}; shift

update_owner_if_needed() {
    target_dir=${1}; shift
    current_user="${USERNAME}"
    current_owner=$(sudo -u ${current_user} ls -ld ${target_dir} | awk '{print $3}')
    if [[ "${current_owner}" == "${current_user}" ]]; then
        echo "OK: ${target_dir} owner is as expected (${current_user})"
        return 0
    fi
    echo "CHOWN: changing ${target_dir} owner from ${current_owner} to ${current_user}"
    sudo chown -R ${current_user}:${current_user} ${target_dir}
}

for target_dir in "/workspace" "/commandhistory" "/home/${USERNAME}/.claude"; do
    update_owner_if_needed "${target_dir}"
done
