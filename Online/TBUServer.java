package Online;

public class TBUServer {
    Server onlineServ;
    Server interServ;
    public TBUServer(){
        onlineServ = new Server(1102);
        interServ = new Server(25564);
        
    }

    public void start(){
        onlineServ.start();
        interServ.start();
    }
}
