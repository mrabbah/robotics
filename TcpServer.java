package com.choranet.magideutz.tcpudpservers;


import java.io.IOException;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author RABBAH
 */
public class TcpServer extends Thread {

    private static String _message = "Hello I'm your TCP server.";
    private static int _port = 7777;
    private static ServerSocket _socket;

    @Override
    public void run() {
        try {
            _socket = new ServerSocket(_port);
            System.out.println("TCP server is running on " + _port + "...");
            while (true) {
                // Accept new TCP client
                Socket client = _socket.accept();
                // Open output stream
                OutputStream output = client.getOutputStream();

                System.out.println("New TCP client, address " + client.getInetAddress() + " on " + client.getPort() + ".");

                // Write the message and close the connection
                output.write(_message.getBytes());
                client.close();
            }
        } catch (IOException ex) {
            Logger.getLogger(TcpServer.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

}//class