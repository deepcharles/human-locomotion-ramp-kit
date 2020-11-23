"""Fetcher for RAMP data stored in OSF

To adapt it for another challenge, change the CHALLENGE_NAME and upload
public/private data as `tar.gz` archives in dedicated OSF folders named after
the challenge.
"""
import tarfile
from pathlib import Path
from osfclient.api import OSF
from osfclient.exceptions import UnauthorizedException

LOCAL_DATA = Path(__file__).parent / "data"

CHALLENGE_NAME = 'human_locomotion'
RAMP_FOLDER_CONFIGURATION = {
    'public': dict(code='t4uf8', archive_name='public.tar.gz'),
    'private': dict(code='vw8sh', archive_name='private.tar.gz'),
}
DOWNLOAD_URL = "https://plmbox.math.cnrs.fr/f/8224e749026747758c56/?dl=1"


def get_connection_info(get_private, username=None, password=None):
    "Get connection to OSF and info relative to public/private data."
    if get_private:
        osf, folder_name = OSF(username=username, password=password), 'private'
    else:
        assert username is None and password is None, (
            "Username and password should only be provided when fetching "
            "private data."
        )
        osf, folder_name = OSF(), 'public'
    data_config = RAMP_FOLDER_CONFIGURATION[folder_name]

    try:
        project = osf.project(data_config['code'])
        store = project.storage('osfstorage')
    except UnauthorizedException:
        raise ValueError("Invalid credentials for RAMP private storage.")
    return store, data_config


def get_one_element(container, name):
    "Get one element from OSF container with a comprehensible failure error."
    elements = [f for f in container if f.name == name]
    container_name = (
        container.name if hasattr(container, 'name') else CHALLENGE_NAME
    )
    assert len(elements) == 1, (
        f'There is no element named {name} in {container_name} from the RAMP '
        'OSF account.'
    )
    return elements[0]


def check_data_exists(private):
    # TODO: add a checksum for the data folder to check public/private
    # for now we just check that some files are present in the directory.
    return LOCAL_DATA.exists and len(list(LOCAL_DATA.glob('*'))) != 0


def download_from_osf(private, username=None, password=None):
    "Download and uncompress the data from OSF."

    if not check_data_exists():
        LOCAL_DATA.mkdir(exist_ok=True)

        # Get the connection to OSF
        store, data_config = get_connection_info(
            private, username=username, password=password
        )

        # Find the folder in the OSF project
        print("Checking the data URL...", end='', flush=True)
        challenge_folder = get_one_element(store.folders, CHALLENGE_NAME)

        # Find the file to download from the OSF project
        archive_name = data_config['archive_name']
        osf_file = get_one_element(challenge_folder.files, archive_name)
        print('Ok.')

        # Download the archive in the data
        ARCHIVE_PATH = LOCAL_DATA / archive_name
        print("Downloading the data...")
        with open(ARCHIVE_PATH, 'wb') as f:
            osf_file.write_to(f)

        # Uncompress the data in the data folder
        print("Extracting now...", end="", flush=True)
        with tarfile.open(ARCHIVE_PATH) as tf:
            tf.extractall(LOCAL_DATA)
        print("Ok.")

        # Clean the directory by removing the archive
        print("Removing the archive...", end="", flush=True)
        ARCHIVE_PATH.unlink()
        print("Ok.")
    else:
        print("Data is already present on the system. If you want to reload "
              f"the data, please delete or move the folder {LOCAL_DATA}.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description=f'Data loader for the {CHALLENGE_NAME} challenge on RAMP.'
    )
    parser.add_argument('--private', action='store_true',
                        help='If this flag is used, download the private data '
                        'from OSF. This requires the username and password '
                        'options to be provided.')
    parser.add_argument('--username', type=str, default=None,
                        help='Username for downloading private OSF data.')
    parser.add_argument('--password', type=str, default=None,
                        help='Password for downloading private OSF data.')
    args = parser.parse_args()

    download_from_osf(args.private, args.username, args.password)
