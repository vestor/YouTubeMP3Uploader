import glob
import unicodedata
from os.path import basename, splitext
import os
import converter
import uploader
from uploader import *


def normalize_caseless(text):
    return unicodedata.normalize("NFKD", text.casefold())


def caseless_equal(left, right):
    return normalize_caseless(left) == normalize_caseless(right)


def create_and_upload_video(audio_file, options, folder_name):
    base_filename = splitext(basename(audio_file))[0]
    video_name = folder_name + '.mp4'
    saved_temp_video = converter.convert_to_mp4(audio_file=audio_file, name=video_name, image_file=options.imageFile)
    uploaded_video_id = uploader.initialize_upload(youtube, playstlist_title=options.playlistTitle,
                                                   file_name=saved_temp_video, category=options.category,
                                                   privacy_status=options.privacyStatus, keywords=options.keywords,
                                                   title=base_filename)
    os.remove(saved_temp_video)
    return uploaded_video_id


if __name__ == '__main__':
    argparser.add_argument("--folder", required=True, help="Path of the root directory")
    argparser.add_argument("--playlistTitle",
                           help="Name of your playlist in Youtube. It will be created if it does not exist")
    argparser.add_argument("--imageFile", default=None, help="Path to the image to be used in the video")
    argparser.add_argument("--category", default="10", help="Numeric video category. If its a music video use 10")
    argparser.add_argument("--keywords", help="Video keywords, comma separated", default="")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES, default=VALID_PRIVACY_STATUSES[0],
                           help="Video privacy status.")
    argparser.add_argument("--clientFile", default="client_secret.json", help="Location of the client secret file. See https://developers.google.com/api-client-library/python/auth/web-app")
    argparser.add_argument("--skipFolderRange", default=None,
                           help="Specify the range of folders to skip. Ex: 1..10 or 1,2,4 or abc,cdef,1..100")
    argparser.add_argument("--startingFolder", default=None,
                           help="Specify the folder number to start from. Ex. 1")
    argparser.add_argument("--uploadAllFiles", default=True, help="Should the script consider to upload all the files inside a folder or consider only the latest one. Defaults to all files.")
    args = argparser.parse_args()

    folders_to_skip = []
    if args.skipFolderRange:
        uniques = args.skipFolderRange.split(",")
        for unique in uniques:
            if ".." in unique:
                start_end = unique.split("..")
                print start_end
                folders_to_skip.extend(str(x) for x in range(int(start_end[0]), int(start_end[1]) + 1))
            else:
                folders_to_skip.append(unique)

    if args.startingFolder:
        folders_to_skip.extend(str(x) for x in range(int(args.startingFolder) + 1))

    if not os.path.exists(args.folder):
        exit("Please specify a valid file using the --folder= parameter.")

    path = os.path.abspath(args.folder)
    youtube = get_authenticated_service(args)

    folders = next(os.walk(path))[1]

    for folder in folders:
        if folder in folders_to_skip:
            print 'Skipping folder ' + folder + '\n'
            continue

        if not args.uploadAllFiles:
            file = max(files_in_folder = glob.glob(path + '/' + folder + '/*.mp3'), key=os.path.getctime)
            create_and_upload_video(file, args, folder)
        else:
            files_in_folder = glob.glob(path + '/' + folder + '/*.mp3')
            for file in files_in_folder:
                create_and_upload_video(file, args, folder)
