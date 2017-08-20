package com.choranet.magideutz.tcpudpservers;


import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.SocketException;
import java.util.logging.Level;
import java.util.logging.Logger;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
/**
 *
 * @author RABBAH
 */
public class UdpServer extends Thread {

    final static int port = 5555;
    final static int taille = 1024;
    final static byte buffer[] = new byte[taille];

    @Override
    public void run() {
        try {
            DatagramSocket socket = new DatagramSocket(port);
            System.out.println("Serveur udp start at port " + port + " ....");
            while (true) {
                DatagramPacket data = new DatagramPacket(buffer, buffer.length);
                socket.receive(data);
                System.out.println("Reception packet udp : "  + data.getAddress());
                socket.send(data);
            }
        } catch (SocketException ex) {
            Logger.getLogger(UdpServer.class.getName()).log(Level.SEVERE, null, ex);
        } catch(IOException ioe) {
            Logger.getLogger(UdpServer.class.getName()).log(Level.SEVERE, null, ioe);
        }
    }
   
}
