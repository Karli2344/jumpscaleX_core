from Jumpscale import j

from .WireGuard import WireGuard

from nacl import public
from nacl.signing import VerifyKey, SigningKey
from nacl.encoding import Base64Encoder
from nacl.public import SealedBox

import netaddr


class WGFactory(j.baseclasses.object_config_collection_testtools):
    """
    wireguard factory

    works over ssh

    """

    __jslocation__ = "j.tools.wireguard"
    _CHILDCLASS = WireGuard

    def get_by_id(self, id):
        data = self._model.get(id)
        if j.tools.wireguard.exists(data.name):
            return self.get(data.name)

    def generate_zos_keys(self, node_public_key):
        """
        Generate a new set of wireguard key pair and encrypt
        the private side using the public key of a 0-OS node.

        This implementation match the format 0-OS except to be able
        to read wireguard keys into network reservations.

        :param node_public_key: hex encoded public key of 0-OS node.
                                This is the format you find in the explorer
        :type node_public_key: str
        :return: tuple containing 3 fields (private key, private key encrypted, public key)
        :rtype: typle
        """
        wg_private = public.PrivateKey.generate()
        wg_public = wg_private.public_key

        wg_private_base64 = wg_private.encode(Base64Encoder)
        wg_public_base64 = wg_public.encode(Base64Encoder)

        node_public_bin = j.data.hash.hex2bin(node_public_key)
        node_public = VerifyKey(node_public_bin)
        box = SealedBox(node_public.to_curve25519_public_key())

        wg_private_encrypted = box.encrypt(wg_private_base64)
        wg_private_encrypted_hex = j.data.hash.bin2hex(wg_private_encrypted)

        return (wg_private_base64.decode(), wg_private_encrypted_hex.decode(), wg_public_base64.decode())

    def test(self):
        """
        kosmos -p 'j.tools.wireguard.test()'
        :return:
        """
        # setup server on a digital ocean client
        print("Configuring server")
        wgs = self.get(name="test5", sshclient_name="do", network_private="10.5.0.1/24")
        wgs.sshclient_name = "do"
        wgs.interface_name = "wg-test"
        wgs.network_private = "10.5.0.1/24"
        wgs.network_public = wgs.executor.sshclient.addr
        wgs.save()

        # configure local client
        print("Configuring local client")
        wg = self.get(name="local", sshclient_name="myhost")
        wg.network_private = "10.5.0.2/24"
        wg.port = 7778
        wg.interface_name = "wg-test"
        wg.peer_add(wgs)
        wg.save()

        print("Adding client to server")
        wgs.peer_add(wg)
        wgs.save()

        print("Install server")
        wgs.install()
        wgs.configure()

        print("Install client")
        wg.install()
        wg.configure()
