package Online;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class OutputHandler {
    Server host;
    int port;
    private OutputStream out;
    private InputStream in;

    public OutputHandler(Server host, int port) {
        this.port = port;
        this.host = host;
        connectToOutput();

    }

    private void connectToOutput() {
        Runnable r = () -> {
            while (true) {
                try (ServerSocket ss = new ServerSocket(port)) {
                    Socket s = ss.accept();
                    if (out == null && in == null) {
                        this.out = s.getOutputStream();
                        this.in = s.getInputStream();
                        this.startListening();
                    } else {
                        Printer.debugPrint("WTF why would you try to connect more output threads????");
                    }
                    Printer.debugPrint("Output is connected!");
                } catch (IOException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
                try {
                    Thread.sleep(2000);
                } catch (InterruptedException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }
        };
        Thread connector = new Thread(r);

        connector.start();
    }

    public void sendPacket(Packet p) {
        Printer.debugPrint("Sending to output side" + p);
        try {
            String msg = p.toJSONString();
            if (out != null)
                out.write(p.toJSONString().getBytes(StandardCharsets.UTF_8), 0, msg.length());
        } catch (IOException e) {
            disconnectRemote();
        }
    }

    private void disconnectRemote() {
        out = null;
        in = null;
    }

    public void startListening() {
        Thread listener = new Thread(() -> {
            while (true) {
                byte[] bmsg = new byte[1024];
                try {
                    in.read(bmsg, 0, 1024);
                    String msg = new String(bmsg, StandardCharsets.UTF_8);
                    System.out.println("Message recieved from output: " + msg);
                    Packet p = Packet.fromJSONString(msg);
                    host.sendPacketToAllClients(p);
                } catch (IOException e) {
                    disconnectRemote();
                }

                try {
                    Thread.sleep(1000 / 60);
                } catch (InterruptedException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }
        });
        listener.start();
    }
}
