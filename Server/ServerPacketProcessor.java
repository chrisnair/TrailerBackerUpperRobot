package Online;

import java.util.Map;
import java.util.UUID;
import java.awt.image.BufferedImage;

/**
 * Packet processor meant for the ClientHandlers that the Server class aggregates
 *
 * @author Joshua Bergthold
 */
public class ServerPacketProcessor extends PacketProcessor{

    ClientHandler ch;
    public ServerPacketProcessor(ClientHandler host) {
        super(host);
        ch = host;
    }

    @Override
    public void executePacket(Packet p){
        Printer.debugPrint("ServerPP level: " + p.toShortenedString());
        switch(p.getCommand().getType()) {
            case DefaultOnlineCommands.SIMPLE_TEXT:
                Printer.printIfVerbose("Distributing text message: " + Packet.shortenedID(p.getPacketID()));
                ch.sendForServerToDistribute(p);
                return;
            case DefaultOnlineCommands.CONTROL_SIGNAL:
                switch(p.getCommand().getCommandLine(1)) {
                    case DefaultOnlineCommands.THROTTLE:
                        System.out.println((double)p.getData());
                        return;
                    case DefaultOnlineCommands.STEERING_ANGLE:
                        System.out.println((double)p.getData());
                        return;
                    case DefaultOnlineCommands.GYRO_READING:
                        System.out.println((double)p.getData());
                        return;
                }
            case DefaultOnlineCommands.QUIT:

        }

        super.executePacket(p);
    }

}
