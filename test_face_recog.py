import os
import pickle
from pprint import pprint

import boto3
import face_recognition
import numpy as np

videos = os.listdir(os.path.join("test_cases", "test_case_1"))

print(videos[0])
input_video_file_path = os.path.join("test_cases", "test_case_1", videos[0])

path = "tmp/"

if not os.path.exists(path):
    os.mkdir(path)

os.system(
    "ffmpeg -i "
    + str(input_video_file_path)
    + " -r 1 "
    + str(path)
    + "image_%3d.jpeg"
)

# Detect faces from the frames.
frames = os.listdir(path)

faces = []
with open("encoding", "rb") as f:
    encoding = pickle.load(f)

for frame in frames:
    image = face_recognition.load_image_file(os.path.join(path, frame))
    face_encoding_data = face_recognition.face_encodings(image)[0]
    face_name = face_recognition.compare_faces(
        face_encoding_data, encoding["encoding"]
    )
    print(face_name)


pprint(encoding, depth=10)

# encodings = np.fromfile("encoding")

# # Get the name of the first detected face.
# face_name = None
# if faces:
#     face_name = face_recognition.compare_faces(faces[0], encoding)

# # Search for the student's academic information in DynamoDB.
# dynamodb = boto3.resource("dynamodb")
# table = dynamodb.Table("student_data")
# student_data = table.get_item(Key={"name": face_name})["Item"]

# # Store the student's academic information as a CSV file in the output bucket.
# output_bucket = boto3.resource("s3").Bucket("output-bucket")
# output_file_path = f"{input_video_file_path}.csv"
# with open(output_file_path, "w") as output_file:
#     output_file.write(
#         f'{student_data["name"]},{student_data["major"]},{student_data["year"]}'
#     )

# # Upload the CSV file to the output bucket.
# output_bucket.upload_file(output_file_path, output_file_path)

# return {
#     "statusCode": 200,
#     "body": json.dumps("Student information saved successfully!"),
# }
