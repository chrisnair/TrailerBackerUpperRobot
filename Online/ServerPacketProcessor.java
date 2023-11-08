package Online;

import java.util.Map;
import java.util.UUID;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

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
            case DefaultOnlineCommands.CONTROL_SINGAL:
                switch (p.getCommand().getCommandLine(1)) {
                    case DefaultOnlineCommands.STEERING_ANGLE : {
                        System.out.println("Steering angle: " + p.getData());
                        writePacketDataToFile(p, "steering_angle.tbu");
                        return;
                    }
                    case DefaultOnlineCommands.THROTTLE:{
                        System.out.println((double)p.getData());
                        writePacketDataToFile(p, "drive_power.tbu");
                        return;
                    }
                }
            case DefaultOnlineCommands.INFO:
                switch (p.getCommand().getCommandLine(1)) {
                    case DefaultOnlineCommands.PICTURE:{
                        //System.out.println((BufferedImage)p.getData());
                        return;
                    }
                }

            case DefaultOnlineCommands.QUIT:

        }

        super.executePacket(p);
    }

    public void writePacketDataToFile(Packet p, String filename){
        File outputFile = new File("/tbu_data/"+filename);
                        try {
                            FileWriter writer = new FileWriter(outputFile);
                            writer.write(p.getData().toString());
                            writer.close();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
    }

}
