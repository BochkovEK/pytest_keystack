# pytest_keystack
## Set certificate in cloud.yaml:

<code>&lt;cloud_name&gt;:<br>
&nbsp;&nbsp;&nbsp;&nbsp;auth:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;...<br>
&nbsp;&nbsp;&nbsp;&nbsp;cacert: <./crt/path>
</code>

## Get crt from cloud:
### lcm installation:
/installer/data/ca/cert/chain-cert.pem
### gitlab.itkey installation:
http://10.224.38.220:8200/ui/vault/secrets/secret_v2/show/deployments/itkey/dev/ebochkov-ks-sber/ssl_certificates/haproxy_pem 