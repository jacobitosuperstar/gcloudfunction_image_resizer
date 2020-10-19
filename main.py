import os
import tempfile
from google.cloud import storage
from wand.image import Image

storage_client = storage.Client()
PREFIX = "modificado"


def image_reziser(event, context):
    """
    Changes the sizes of the images uploaded to the google_bucket and
    deletes the original blob once the process is finished

    LAS VARIABLES QUE PODEMOS SACAR DEL EVENTO DE CARGA
    context.event_id
    context.event_type
    event['bucket']
    event['name']
    event['metageneration']
    event['timeCreated']
    event['updated']
    """

    file_data = event

    file_name = file_data['name']
    print(f"el nombre de los datos es: {file_name}")
    bucket_name = file_data['bucket']
    print(f"el nombre del bucket es: {bucket_name}")

    blob = storage_client.bucket(bucket_name).get_blob(file_name)

    if file_name.startswith(PREFIX):
        print("La imagen no necesita ser modificada")
        return

    # Creando la carpeta de archivos temporal.
    _, temp_local_filename = tempfile.mkstemp()
    blob.download_to_filename(temp_local_filename)
    print(f"Imagen descargada al {temp_local_filename}")

    with Image(filename=temp_local_filename) as image:
        # When image height is greater than its width
        if image.height > image.width:
            image.crop(width=image.width, height=image.width, gravity="center")
            image.resize(500, 500)

        # When image width is greater than its height
        elif image.width > image.height:
            image.crop(width=image.height,
                       height=image.height,
                       gravity="center")
            image.resize(500, 500)

        # any other case
        else:
            image.resize(500, 500)

        image.enhance()
        image.save(filename=temp_local_filename)
    print("Imagen modificada")

    modifiedimage_bucket = storage_client.bucket(bucket_name)
    new_blob = modifiedimage_bucket.blob(f"{PREFIX}-{file_name}")
    new_blob.upload_from_filename(temp_local_filename)
    print("Imagen modificada y guardada")
    print(f"el id del proceso es {context.event_id}")
    print(f"el tipo de vento es {context.event_type}")

    # Eliminar directorio temporal de archivos.
    os.remove(temp_local_filename)
    # Eliminando el blob original
    bucket_name.delete_blob(file_name)
