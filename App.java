package com.choranet.magideutz.tcpudpservers;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void main( String[] args )
    {
        TcpServer tcp = new TcpServer();
        UdpServer udp = new UdpServer();
        tcp.start();
        udp.start();
    }
}
