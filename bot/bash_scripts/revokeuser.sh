#!/bin/bash

client=$1
group_name="nogroup"
cd /etc/openvpn/server/easy-rsa/
./easyrsa --batch revoke "$client"
EASYRSA_CRL_DAYS=3650 ./easyrsa gen-crl
rm -f /etc/openvpn/server/crl.pem
cp /etc/openvpn/server/easy-rsa/pki/crl.pem /etc/openvpn/server/crl.pem
# CRL is read with each client connection, when OpenVPN is dropped to nobody
chown nobody:"$group_name" /etc/openvpn/server/crl.pem
exit