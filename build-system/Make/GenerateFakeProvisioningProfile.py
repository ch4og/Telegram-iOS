#!/usr/bin/env python3

import argparse
import pathlib
import plistlib
import subprocess
import tempfile


def run_output(arguments):
    return subprocess.check_output(arguments)


def rewrite_profile(source_path, destination_path, bundle_id, team_id, certificate_path, keychain, identity):
    profile_data = run_output([
        "security",
        "cms",
        "-D",
        "-i",
        str(source_path),
    ])
    profile = plistlib.loads(profile_data)
    entitlements = profile.setdefault("Entitlements", {})
    application_identifier = "{}.{}".format(team_id, bundle_id)

    entitlements["application-identifier"] = application_identifier
    entitlements["com.apple.developer.team-identifier"] = team_id
    if "keychain-access-groups" in entitlements:
        entitlements["keychain-access-groups"] = [application_identifier]
    if "com.apple.security.application-groups" in entitlements:
        entitlements["com.apple.security.application-groups"] = ["group.{}".format(bundle_id)]
    if "aps-environment" not in entitlements:
        entitlements["aps-environment"] = "development"

    profile["ApplicationIdentifierPrefix"] = [team_id]
    profile["TeamIdentifier"] = [team_id]
    profile["AppIDName"] = bundle_id
    profile["Name"] = "iOS Team Provisioning Profile: {}".format(bundle_id)
    profile["DeveloperCertificates"] = [pathlib.Path(certificate_path).read_bytes()]
    profile.pop("DER-Encoded-Profile", None)

    with tempfile.NamedTemporaryFile(suffix=".plist", delete=False) as temporary_file:
        temporary_path = pathlib.Path(temporary_file.name)
    try:
        with temporary_path.open("wb") as file:
            plistlib.dump(profile, file, fmt=plistlib.FMT_XML, sort_keys=False)
        subprocess.check_call([
            "security",
            "cms",
            "-S",
            "-k",
            keychain,
            "-N",
            identity,
            "-i",
            str(temporary_path),
            "-o",
            str(destination_path),
        ])
    finally:
        temporary_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Create a fake profile for an unsigned AltStore build")
    parser.add_argument("--source", required=True, type=pathlib.Path)
    parser.add_argument("--destination", required=True, type=pathlib.Path)
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--team-id", required=True)
    parser.add_argument("--certificate", required=True, type=pathlib.Path)
    parser.add_argument("--keychain", required=True)
    parser.add_argument("--identity", required=True)
    arguments = parser.parse_args()

    arguments.destination.parent.mkdir(parents=True, exist_ok=True)
    rewrite_profile(
        source_path=arguments.source,
        destination_path=arguments.destination,
        bundle_id=arguments.bundle_id,
        team_id=arguments.team_id,
        certificate_path=arguments.certificate,
        keychain=arguments.keychain,
        identity=arguments.identity,
    )


if __name__ == "__main__":
    main()
