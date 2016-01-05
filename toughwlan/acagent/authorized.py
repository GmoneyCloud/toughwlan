#!/usr/bin/env python
# coding=utf-8
import os
import six
from twisted.internet import protocol, reactor
from txradius import message
from toughlib import logger
from txradius.radius import dictionary
from txradius.radius import packet
from toughwlan.acagent.session import RadiusSession
from toughwlan.acagent.radius_loader import RadiusLoader
import toughwlan

class AcRadiusAuthorize(protocol.DatagramProtocol):
    def __init__(self, config, dbengine=None,log=None):
        self.config = config
        self.dbengine = dbengine
        self.radloader = RadiusLoader(config,dbengine)
        self.log = log or logger.Logger(config)

    def processPacket(self, coareq, (host,port)):
        session_id = coareq.get("Acct-Session-Id",['0'])[0]
        if session_id in RadiusSession.sessions:
            del RadiusSession.sessions[session_id]

        coaresp = coareq.CreateReply()
        self.log.info("[RADIUSAuthorize] :: Send Authorize radius response: %s" % (repr(coaresp)))
        if self.config.acagent.debug:
            self.log.debug(reply.format_str())
        self.transport.write(reply.ReplyPacket(), reply.source)


    def datagramReceived(self, datagram, (host, port)):
        try:
            radius = self.radloader.getRadius(host)
            if not radius:
                self.log.info('[RADIUSAuthorize] :: Dropping Authorize packet from unknown host ' + host)
                return

            coa_req = message.CoaMessage(packet=datagram, dict=radius.dict, secret=six.b(radius.secret))
            self.log.info("[RADIUSAuthorize] :: Received Authorize radius request: %s" % message.format_packet_log(coa_req))

            if self.config.acagent.debug:
                self.log.debug(coa_req.format_str())

            self.processPacket(coa_req)

        except packet.PacketError as err:
            errstr = 'RadiusError:Dropping invalid packet from {0} {1},{2}'.format(
                host, port, utils.safeunicode(err))
            self.log.error(errstr)


def run(config, dbengine=None,log=None):
    authorize_protocol = AcRadiusAuthorize(config, dbengine=dbengine, log=log)
    reactor.listenUDP(
        int(config.acagent.radius.authorize_port), authorize_protocol, interface=config.acagent.host)





