# Securing the Rover

Quick list of things to work on:

1. Establish proper user group permission and provisioning onboard Jetson
	1. user = non-sudo group (not able to issue commands that could impact system performance)
	1. marsrover = sudo (able to issue commands with password)
	1. admin = password less sudo (able to issue sudo commands without password)
	1. root = login as root diabled
1. Setup firewall to restrict access to VPN servers
1. HTTPS/TLS application communication [with tornado](https://stackoverflow.com/questions/18307131/how-to-create-https-tornado-server#18307308)
	1. Create TLS certificates and keys
	1. Self-signed vs Signed by Authority?
1. Authenticated Sessions (Single User) - [Tornado documentation](https://www.tornadoweb.org/en/stable/guide/security.html)
	1. Password protected access to controls
	1. Prevent directory traversal
	1. XSRF protection
	1. DNS Rebinding mitigation
1. Authentication via key exchange (Multi User)
	1. User [Database](https://www.tutorialspoint.com/postgresql/postgresql_create_database.htm)
		1. Encryption
		1. Password hashing
		1. Secure Key storage
	1. Provisioned access
	1. Users authorized for access via key
1. VPN access to Cloud Server
1. Postition and Status monitoring 