#
# code copied from
# http://rocketscience.itteco.org/2010/01/10/sending-cookie-via-xmlrpclib/
# by Nazar Leush
#
# changes added by jesus m. rodriguez
#
import xmlrpclib
from xmlrpclib import ProtocolError, Fault

from Cookie import _quote


class CookieTransport(xmlrpclib.Transport):

    def __init__(self, cookies=None, *args, **kwargs):
        xmlrpclib.Transport.__init__(self, *args, **kwargs)
        self.cookies = cookies

    ##
    # Send a complete request, and parse the response.
    #
    # @param host Target host.
    # @param handler Target PRC handler.
    # @param request_body XML-RPC request body.
    # @param verbose Debugging flag.
    # @return Parsed response.

    def single_request(self, host, handler, request_body, verbose=0):
        # issue XML-RPC request

        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        try:
            self.send_request(h, handler, request_body)
            self.send_host(h, host)
            self.send_user_agent(h)

            # Custom cookies.
            self.send_cookies(h)

            self.send_content(h, request_body)

            response = h.getresponse(buffering=True)
            if response.status == 200:
                self.verbose = verbose
                return self.parse_response(response)
        except Fault:
            raise
        except Exception:
            # All unexpected errors leave connection in
            # a strange state, so we clear it.
            self.close()
            raise

        #discard any response data and raise exception
        if (response.getheader("content-length", 0)):
            response.read()
        raise ProtocolError(
            host + handler,
            response.status, response.reason,
            response.msg,
            )

    def send_cookies(self, connection):
        if self.cookies:
            for k, v in self.cookies.iteritems():
                connection.putheader(
                    "Cookie", ";".join(["%s=%s" % (k, _quote(v))]))
