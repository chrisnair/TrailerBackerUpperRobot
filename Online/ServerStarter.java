package Online;

import java.io.BufferedReader;
import java.io.InputStreamReader;

public class ServerStarter {
    public static void main(String[] args) {
        Server serv = new Server(1102);
        serv.start();

        try {
            // Set the path to your Python interpreter and the path to your Python script
            String pythonInterpreter = "python3";  // Change this if your Python executable has a different name
            String pythonScriptPath = "../TrailerBackerUpperRobot/src/driver.py";  // Update this with the actual path

            // Build the command to run the Python script
            ProcessBuilder processBuilder = new ProcessBuilder(pythonInterpreter, pythonScriptPath);
            
            // Start the process
            Process process = processBuilder.start();

            // Read the output of the Python script (if any)
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }

        Printer.toggleDebugosity();
        Printer.toggleVerbosity();
    
        } catch (Exception e){
            e.printStackTrace();
        }
    }
}
