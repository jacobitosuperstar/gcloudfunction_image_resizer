if self.cutter is True:
    # print(self.image.name)
    blob = storage_client.bucket(bucket_name).get_blob(self.image.name)
    _, temp_local_filename = tempfile.mkstemp()
    blob.download_to_filename(temp_local_filename)

    # print('Imagen descargada a la carpeta temporal.')

    with Image(filename=temp_local_filename) as image:

        # When image height is greater than its width
        if image.height > image.width:
            image.crop(width=image.width,
                       height=image.width,
                       gravity='center")
            image.resize(1000, 1000)

        # When image width is greater than its height
        elif image.width > image.height:
            image.crop(width=image.height,
                       height=image.height,
                       gravity='center')
            image.resize(1000, 1000)

        # any other case
        else:
            image.resize(1000, 1000)

        image.format = 'jpeg'
        image.enhance()
        image.save(filename=temp_local_filename)

    # print(f'Imagen {self.image.name} fue modificada.')

    modifiedimage_bucket = storage_client.bucket(bucket_name)
    new_blob = modifiedimage_bucket.blob(self.image.name)
    new_blob.upload_from_filename(temp_local_filename)
    # print('Imagen modificada y cargada')

    # Eliminar directorio temporal de archivos.
    os.remove(temp_local_filename)
    # retornando el cortador a su estado original
    self.cutter = False
    self.save()
    # print('revisar')

