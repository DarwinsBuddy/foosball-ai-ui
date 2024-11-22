SSL_DIR="web/assets/ssl"

# Setup ssl
rm -fR "${SSL_DIR:?}/*" &&
openssl req -new -x509 -days 365 -nodes -out "${SSL_DIR}/server.pem" -keyout "${SSL_DIR}/server.key" -config "${SSL_DIR}/san.cnf" &&
openssl x509 -noout -text -in "${SSL_DIR}/server.pem"