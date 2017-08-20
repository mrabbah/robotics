/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package abc;

import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;
import java.awt.image.RenderedImage;
import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.imageio.ImageIO;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.MatOfRect;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.highgui.VideoCapture;
import org.opencv.objdetect.CascadeClassifier;

/**
 *
 * @author OldSpice
 */
public class TestWebCam extends JPanel implements ActionListener {

    private BufferedImage image;
    private JButton button = new JButton("capture");
    int count = 1;

    public TestWebCam() {
        super();
        button.addActionListener((ActionListener) this);
        this.add(button);
    }

    private BufferedImage getimage() {
        return image;
    }

    private void setimage(BufferedImage newimage) {
        image = newimage;
    }

    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        if (this.image == null) {
            return;
        }
        g.drawImage(this.image, 0, 0, this.image.getWidth(), this.image.getHeight(), null);
    }

    public static void main(String args[]) throws Exception {
        JFrame frame = new JFrame("Face Recognizer");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400, 380);
        System.loadLibrary("opencv_java2412");
        //CascadeClassifier faceDetector=new CascadeClassifier("C:\\opencv\\sources\\data\\lbpcascades\\lbpcascade_silverware.xml");
        //CascadeClassifier faceDetector=new CascadeClassifier("C:\\opencv\\sources\\data\\lbpcascades\\lbpcascade_profileface.xml");
        //CascadeClassifier faceDetector = new CascadeClassifier("C:\\opencv\\sources\\data\\lbpcascades\\lbpcascade_frontalface.xml");
        CascadeClassifier faceDetector = new CascadeClassifier("/usr/local/Cellar/opencv/2.4.12_2/share/OpenCV/lbpcascades/lbpcascade_frontalface.xml");
        TestWebCam toc = new TestWebCam();

        frame.add(toc);;
        frame.setVisible(true);
        Mat webcam_image = new Mat();
        MatToBufImg mat2Buf = new MatToBufImg();
        VideoCapture capture = null;
        try {
            capture = new VideoCapture(0);
        } catch (Exception xx) {
            xx.printStackTrace();
        }
        if (capture.open(0)) {
            while (true) {
                capture.read(webcam_image);
                if (!webcam_image.empty()) {
                    frame.setSize(webcam_image.width(), webcam_image.height());
                    MatOfRect faceDetections = new MatOfRect();
                    faceDetector.detectMultiScale(webcam_image, faceDetections);
                    for (Rect rect : faceDetections.toArray()) {
                        Core.rectangle(webcam_image, new Point(rect.x, rect.y), new Point(rect.x + rect.width, rect.y + rect.height), new Scalar(0, 255, 0));// mat2Buf, mat2Buf);
                    }
                    System.out.println("...............face detected: " + faceDetections.toArray().length);
                    if (faceDetections.toArray().length == 0) {
                        System.out.println("Sorry Face not detected!");
                    }
                    mat2Buf.setMatrix(webcam_image, ".jpg");
                    toc.setimage(mat2Buf.getBufferedImage());
                    toc.repaint();
                } else {
                    System.out.println("problems with webcam image capture");
                    break;
                }
            }
        }
        capture.release();
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        System.out.println("hellohellohellohellohello");
        String ans = JOptionPane.showInputDialog(null, "Color/Grey");
        System.out.println(ans);
        BufferedImage bi = image;
        ImageIcon ii = null;
        ii = new ImageIcon(bi);
        Image newimg = bi.getScaledInstance(320, 220, java.awt.Image.SCALE_SMOOTH);
        ii = new ImageIcon(newimg);
        Image i2 = ii.getImage();
        image = new BufferedImage(i2.getWidth(null), i2.getHeight(null), BufferedImage.SCALE_SMOOTH);
        image.getGraphics().drawImage(i2, 0, 0, null);
        RenderedImage rendered = null;
        if (i2 instanceof RenderedImage) {
            rendered = (RenderedImage) i2;
        } else {
            BufferedImage buffered = null;
            if (!ans.equalsIgnoreCase("color")) {
                buffered = new BufferedImage(
                        ii.getIconWidth(),
                        ii.getIconHeight(),
                        BufferedImage.TYPE_BYTE_GRAY);
            } else {
                buffered = new BufferedImage(
                        ii.getIconWidth(),
                        ii.getIconHeight(),
                        BufferedImage.SCALE_SMOOTH);
            }
            Graphics2D g = buffered.createGraphics();
            g.drawImage(i2, 0, 0, null);
            g.dispose();
            rendered = buffered;
        }
        try {
            ImageIO.write(rendered, "JPEG", new File("/Users/rabbah/saved.jpg"));
        } catch (Exception ex) {
        }
    }
}