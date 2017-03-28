import glob
import unicodedata
from os.path import basename, splitext

import converter
import uploader
from uploader import *


def normalize_caseless(text):
    return unicodedata.normalize("NFKD", text.casefold())


def caseless_equal(left, right):
    return normalize_caseless(left) == normalize_caseless(right)


if __name__ == '__main__':
    argparser.add_argument("--folder", required=True, help="Path of the root directory")
    argparser.add_argument("--playlistTitle",
                           help="Name of your playlist in Youtube. It will be created if it does not exist")
    argparser.add_argument("--imageFile", default=None, help="Path to the image to be used in the video")
    argparser.add_argument("--category", default="10", help="Numeric video category. If its a music video use 10")
    argparser.add_argument("--keywords", help="Video keywords, comma separated", default="")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES, default=VALID_PRIVACY_STATUSES[0],
                           help="Video privacy status.")
    argparser.add_argument("--clientFile", default="client_secret.json", help="Location of the client secret file. See ")
    args = argparser.parse_args()

    if not os.path.exists(args.folder):
        exit("Please specify a valid file using the --folder= parameter.")

    path = os.path.abspath(args.folder)
    youtube = get_authenticated_service(args)

    folders = next(os.walk(path))[1]

    for folder in folders:
        files_in_folder = glob.glob(path + '/' + folder + '/*.mp3')
        for file in files_in_folder:
            base_filename = splitext(basename(file))[0]
            video_name = base_filename + '.mp4'
            saved_temp_video = converter.convert_to_mp4(audio_file=file, name=video_name, image_file=args.imageFile)

            uploaded_video_id = uploader.initialize_upload(youtube, playstlist_title=args.playlistTitle,
                                                           file_name=saved_temp_video, category=args.category,
                                                           privacy_status=args.privacyStatus, keywords=args.keywords,
                                                           title=base_filename)

            os.remove(saved_temp_video)
