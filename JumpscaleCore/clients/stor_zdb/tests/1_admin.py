from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.clients.zdb._tests_run(name="admin")'

    """

    c = j.servers.zdb.test_instance.client_admin_get()
    c.reset()

    c.namespaces_list()
    assert c.namespaces_list() == ["default"]

    c.namespace_new("test_namespace")
    assert c.namespace_exists("test_namespace")
    assert c.namespaces_list() == ["default", "test_namespace"]

    c.namespace_delete("test_namespace")
    assert c.namespaces_list() == ["default"]

    c.namespace_new("test_namespace")
    c.reset()
    assert c.namespaces_list() == ["default"]

    self._log_info("test ok")

    return "OK"
