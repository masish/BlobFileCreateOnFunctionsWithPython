import logging,os, uuid, shutil

import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('Python HTTP trigger function processed a request.')

        connect_str = str(os.environ.get('STORAGE_CONNECTION_STRING'))

        logging.info("Azure Storage connection string::" + connect_str )

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = str(uuid.uuid4())
        container_client = blob_service_client.create_container(container_name)

        # Create a local directory to hold blob data
        local_path = "/home/site/data"
        if os.path.isdir(local_path):
            shutil.rmtree(local_path)
        os.makedirs(local_path)

        # Create a file in the local data directory to upload and download
        local_file_name = str(uuid.uuid4()) + ".txt"
        upload_file_path = os.path.join(local_path, local_file_name)

        # Write text to the file
        file = open(upload_file_path, 'w')
        file.write("Hello, World!")
        file.close()

        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

        logging.info("Uploading to Azure Storage as blob:" + local_file_name)

        # Upload the created file
        with open(upload_file_path, "rb") as data:
            blob_client.upload_blob(data)

        name = ""

        # List the blobs in the container
        logging.info("Listing blobs...")
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            logging.info(blob.name)
            name = str(blob.name)

        if name:
            return func.HttpResponse(f"Text file , {name}. is created successfully.")
        else:
            return func.HttpResponse(
                "No File made.",
                status_code=200
            )

    except Exception as ex:
        print('Exception:')
        return func.HttpResponse(str(ex))
