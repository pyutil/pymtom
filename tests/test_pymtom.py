# I have used a test during development, however it was integrated into a different project
#   and has required SoapUI for mocking.
# I add as example (of testing or usage)

# def test_mtom_create():
#     files = ["/home/mirek/tmp/black.png"]

#     # mock = False
#     mock = True

#     if mock:
#         # mocked
#         client = zeep.Client(
#             "~/w/pysoap/_other/test.wsdl",
#             transport=MTOMTransport(files=files)
#         )
#         client.service._binding_options["address"] = (
#             "http://localhost:8088/mockimageIOSOAPBinding"
#         )
#     else:
#         # real service (thats a pain: where to take a open and correct service for development?)
#         client = zeep.Client(
#             "https://service.url",
#             transport=MTOMTransport(files=files),
#         )

#     params = {
#         "fileName": "testing_im_sorry.png",
#         "imageData": "cid:{cid}",
#     }

#     client.service.upload(**params)
