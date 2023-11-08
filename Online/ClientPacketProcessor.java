package Online;

/**
 * An implementation of the PacketProcessor class that the Client class uses to execute its packets
 * @author Joshua Bergthold
 */
public class ClientPacketProcessor extends PacketProcessor{

    /**
     * Creates a ClientPacketProcessor with the given Client as its host
     * @param host Client that this processor communicates with
     */
    public ClientPacketProcessor(Client host) {
        super(host);
    }


    @Override
    public void executePacket(Packet p){
        if(p == null){
            return;
        }
        switch(p.getCommand().getType()){
            case DefaultOnlineCommands.SIMPLE_TEXT:
                if(!p.getAuthorID().equals(host.getID())){
                    System.out.println("Message from " + Packet.shortenedID(p.getAuthorID())+ ": " + p.getData());
                }


                return;
        }
        super.executePacket(p);

    }
}
