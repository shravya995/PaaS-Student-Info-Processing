import csv
import os
import pickle

import boto3
import face_recognition
from boto3 import client as boto3_client

s3 = boto3.client("s3")

input_bucket = "quiz-on-friday-project-2-input-data"
output_bucket = "quiz-on-friday-project-2-output-data"


def search_database_table(attribute_value):
    table_name = "CSE546-student-database"
    database = boto3.resource("dynamodb")
    table = database.Table(table_name)  # type: ignore

    response = table.scan(FilterExpression=Attr("name").eq(attribute_value))  # type: ignore

    return response["Items"][0]


# Function to read the 'encoding' file
def open_encoding(filename):
    file = open(filename, "rb")
    data = pickle.load(file)
    file.close()
    return data


def face_recognition_handler(event, context):
    # Get the bucket name and object key from the event
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    object_key = event["Records"][0]["s3"]["object"]["key"]

    # Download the object from S3 to the Lambda execution environment
    local_filename = "/tmp/" + object_key
    s3.download_file(bucket_name, object_key, local_filename)
    video_file_path = local_filename
    output_path = "output/"
    # Load the known face encodings and names from files

    encodings_dict = open_encoding("encoding")

    # Convert the dictionary to separate lists of known_faces and known_names

    known_faces = list(encodings_dict["encoding"])
    known_names = list(encodings_dict["name"])

    # print(known_faces)
    print(type(known_names))

    test_image_name = object_key.split(".")[0]
    print(os.listdir("/tmp/"))
    # Extract frames from the video using ffmpeg
    os.system(
        f"ffmpeg -i {video_file_path} -r 1 /tmp/{test_image_name}-%3d.jpeg"
    )
    print(os.listdir("output/"))
    # Process each extracted frame
    for i in range(
        1, 100
    ):  # Adjust the range depending on the number of frames extracted
        image_path = f"/tmp/{test_image_name}-{i:03d}.jpeg"
        if os.path.isfile(image_path):
            # Load the image
            unknown_image = face_recognition.load_image_file(image_path)
            print("unknown image alright")
            face_encodings = face_recognition.face_encodings(unknown_image)[0]
            print("unknown image alright")
            matches = face_recognition.compare_faces(
                known_faces, face_encodings
            )
            print(matches)
            name = "Unknown"

            # If there is a match, use the known face's name
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]
                result = search_database_table(name)
                output_file_name = object_key.split(".")[0]
                output = [
                    output_file_name,
                    result["name"],
                    result["major"],
                    result["year"],
                ]
                print(output)

                output_path = output_file_name + ".csv"
                with open("/tmp/" + output_path, mode="w") as file:
                    writer = csv.writer(file)
                    writer.writerow(output)
                # Upload CSV file to S3 bucket
                s3.upload_file(
                    "/tmp/" + output_path, "paas-output-bucket", output_path
                )
                os.remove("/tmp/" + output_path)
                break
