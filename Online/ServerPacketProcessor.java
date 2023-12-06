package Online;

import java.util.Map;
import java.util.UUID;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

/**
 * Packet processor meant for the ClientHandlers that the Server class
 * aggregates
 *
 * @author Joshua Bergthold
 */
public class ServerPacketProcessor extends PacketProcessor {

    ClientHandler ch;

    public ServerPacketProcessor(ClientHandler host) {
        super(host);
        ch = host;
    }

    @Override
    public void executePacket(Packet p) {
        // Printer.debugPrint("ServerPP level: " + p.toShortenedString());
        switch (p.getCommand().getType()) {
            case DefaultOnlineCommands.SIMPLE_TEXT:
                Printer.printIfVerbose("Distributing text message: " + Packet.shortenedID(p.getPacketID()));
                ch.sendForServerToDistribute(p);
                return;
            case DefaultOnlineCommands.CONTROL_SIGNAL:
                    System.out.println("Sending a control signal packet to output");
                    ch.sendPacketToOutput(p);
            case DefaultOnlineCommands.INFO:
                switch (p.getCommand().getCommandLine(1)) {
                    case DefaultOnlineCommands.PICTURE: {
                        // System.out.println((BufferedImage)p.getData());
                        return;
                    }
                }
            case DefaultOnlineCommands.DEBUG:
                switch (p.getCommand().getCommandLine(1)) {
                    case DefaultOnlineCommands.CAMERA_MODE_CHANGE:
                        ch.sendPacketToOutput(p);
                        return;
                }

            case DefaultOnlineCommands.QUIT:

        }

        super.executePacket(p);
    }
}
