from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet

import logging
logging.basicConfig(level=logging.DEBUG)

class SimpleSwitch(app_manager.RyuApp):
    # Supported OpenFlow version for this Ryu application
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        # Initialize the MAC address-to-port mapping per datapath
        self.mac_to_port = {}
        self.logger.info("SimpleSwitch initialized with OpenFlow v1.3 support")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
        Handle switch feature event: initialize the default forwarding rule to send unmatched packets to the controller.
        """
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # Create a rule to send all unmatched packets to the controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        """
        Add a flow entry to the datapath (switch) with the given parameters.
        """
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # Define instructions for the flow entry
        instructions = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        # Create a FlowMod message based on the presence of a buffer ID
        if buffer_id is not None:
            flow_mod = parser.OFPFlowMod(
                datapath=datapath, buffer_id=buffer_id, priority=priority,
                match=match, instructions=instructions
            )
        else:
            flow_mod = parser.OFPFlowMod(
                datapath=datapath, priority=priority, match=match,
                instructions=instructions
            )

        # Send the FlowMod message to the switch
        datapath.send_msg(flow_mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        """
        Handle incoming packets sent to the controller (usually unmatched packets).
        """
        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # Extract input port, and Ethernet protocol data
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        src, dst = eth.src, eth.dst
        dpid = datapath.id

        # Initialize or update the MAC-to-port mapping
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        # Log the packet details for debugging purposes
        self.logger.info("Packet in switch DPID: %s SRC: %s DST: %s IN_PORT: %s", dpid, src, dst, in_port)

        # Determine the appropriate output port
        out_port = self.mac_to_port[dpid].get(dst, ofproto.OFPP_FLOOD)

        # Create an action list based on the chosen output port
        actions = [parser.OFPActionOutput(out_port)]

        # Install a flow to avoid receiving this packet type again at the controller
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)

        # Prepare the PacketOut message to send the packet to the selected output port
        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
        packet_out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions, data=data
        )

        # Send the PacketOut message to the switch
        datapath.send_msg(packet_out)