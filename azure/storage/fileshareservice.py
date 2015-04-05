from azure import (
    WindowsAzureConflictError,
    WindowsAzureError,
    DEFAULT_HTTP_TIMEOUT,
    DEV_QUEUE_HOST,
    QUEUE_SERVICE_HOST_BASE,
    xml_escape,
    _convert_class_to_xml,
    _dont_fail_not_exist,
    _dont_fail_on_exist,
    _get_request_body,
    _int_or_none,
    _parse_response_for_dict_filter,
    _parse_response_for_dict_prefix,
    _str,
    _str_or_none,
    _update_request_uri_query_local_storage,
    _validate_not_none,
    _ERROR_CONFLICT,
    _ETreeXmlToObject,
    FILE_SHARE_SERVICE_HOST_BASE, DEV_FILE_SHARE_HOST)
from azure.http import (
    HTTPRequest,
    HTTP_RESPONSE_NO_CONTENT,
    )
from azure.storage import (
    Queue,
    QueueEnumResults,
    QueueMessagesList,
    StorageServiceProperties,
    _update_storage_queue_header,
    _update_storage_file_share_header)
from azure.storage.storageclient import _StorageClient


class FileShareService(_StorageClient):
    """
    This is the main class for managing file shares
    """
    def __init__(self, account_name=None, account_key=None, protocol='https',
                 host_base=FILE_SHARE_SERVICE_HOST_BASE, dev_host=DEV_FILE_SHARE_HOST,
                 timeout=DEFAULT_HTTP_TIMEOUT):
        '''
        account_name:
            your storage account name, required for all operations.
        account_key:
            your storage account key, required for all operations.
        protocol:
            Optional. Protocol. Defaults to http.
        host_base:
            Optional. Live host base url. Defaults to Azure url. Override this
            for on-premise.
        dev_host:
            Optional. Dev host url. Defaults to localhost.
        timeout:
            Optional. Timeout for the http request, in seconds.
        '''
        super(FileShareService, self).__init__(
            account_name, account_key, protocol, host_base, dev_host, timeout)

    def create_file_share(self, share_name, fail_on_exist=False):
        """
        Creates a file share in the storage account associated with this instance class.
        share_name:
            Name for the file share
        fail_on_exist:
            Throw an exception if this flag is set to True and a file share is encontered with the file share
            specified
        """
        _validate_not_none('share_name', share_name)
        request = self._get_share_request(share_name, 'PUT')
        if not fail_on_exist:
            try:
                self._perform_request(request)
                return True
            except WindowsAzureError as ex:
                _dont_fail_on_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def delete_file_share(self, share_name, fail_not_exist=False):
        """
        Deletes the specified file share
        share_name:
            Name for the file share to delete
        """
        _validate_not_none('share_name', share_name)
        request = self._get_share_request(share_name, 'DELETE')
        if not fail_not_exist:
            try:
                self._perform_request(request)
                return True
            except WindowsAzureError as ex:
                _dont_fail_not_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def get_file_share_properties(self, share_name):
        """

        :param share_name:
        :return:
        """
        _validate_not_none('share_name', share_name)
        request = self._get_share_request(share_name, 'GET')

    def _get_share_request(self, share_name, http_action):
        request = HTTPRequest()
        request.method = http_action
        request.host = self._get_host()
        request.path = '/{0}?restype=share'.format(share_name)
        request.path, request.query = _update_request_uri_query_local_storage(
            request, self.use_local_storage)
        request.headers = _update_storage_file_share_header(
            request, self.account_name, self.account_key)

        return request