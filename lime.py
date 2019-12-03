import numpy as np
import argparse
from matplotlib import pyplot as plt
import SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CS16
import time 

class LimeSDR:
  #at first one has to initialize SDR. Init method sets all preferences and setups the data streams
  def __init__(self, cent_freq, meas_time, rx_bw, fs, channel): #rx_bw - bandwidth, fs - sampling rate
    self.channel = channel
    use_agc = True          # Use or don't use the AGC
    self.freq = cent_freq            # LO tuning frequency in Hz
    self.timeout_us = int(5e6)
    self.N = int(fs * meas_time)               # Number of complex samples per transfer
    self.rx_bits = 12            # The Lime's ADC is 12 bits
    RX1 = 0             # RX1 = 0, RX2 = 1
    RX2 = 1
    self.sdr = SoapySDR.Device(dict(driver="lime")) # Create AIR-T instance
      
    if (len(self.channel) == 2):
      self.sdr.setSampleRate(SOAPY_SDR_RX, RX1, fs)   # Set sample rate
      self.sdr.setSampleRate(SOAPY_SDR_RX, RX2, fs)          
      self.sdr.setGainMode(SOAPY_SDR_RX, RX1, True)   # Set the gain mode
      self.sdr.setGainMode(SOAPY_SDR_RX, RX2, True)
      self.sdr.setGain(SOAPY_SDR_RX, RX1, "TIA", 0) # Set TransImpedance Amplifier gain
      self.sdr.setGain(SOAPY_SDR_RX, RX2, "TIA", 0)    
      self.sdr.setGain(SOAPY_SDR_RX, RX1, "LNA", 0) # Set Low-Noise Amplifier gain
      self.sdr.setGain(SOAPY_SDR_RX, RX2, "LNA", 0)      
      self.sdr.setGain(SOAPY_SDR_RX, RX1, "PGA", 0) # programmable-gain amplifier (PGA)
      self.sdr.setGain(SOAPY_SDR_RX, RX2, "PGA", 0)       
      self.sdr.setGain(SOAPY_SDR_RX, RX1, 0)
      self.sdr.setGain(SOAPY_SDR_RX, RX2, 0) 
      self.sdr.setDCOffsetMode(SOAPY_SDR_RX, 0, False)  
      self.sdr.setDCOffsetMode(SOAPY_SDR_RX, 1, False)
      self.sdr.setFrequency(SOAPY_SDR_RX, RX1, self.freq)         # Tune the LO
      self.sdr.setFrequency(SOAPY_SDR_RX, RX2, self.freq)         # Tune the LO
      self.RX1_buff = np.empty(2 * self.N, np.int16)                 # Create memory buffer for data stream
      self.RX2_buff = np.empty(2 * self.N, np.int16)                 # Create memory buffer for data stream
      self.sdr.setBandwidth(SOAPY_SDR_RX, RX1, rx_bw)
      self.sdr.setBandwidth(SOAPY_SDR_RX, RX2, rx_bw)
      self.sdr.setAntenna(SOAPY_SDR_RX, RX1, "LNAL")
      self.sdr.setAntenna(SOAPY_SDR_RX, RX2, "LNAL")
      # Create data buffer and start streaming samples to it
      self.rx_stream = self.sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16, [RX1, RX2])  # Setup data stream
    
    elif(self.channel[0] == 1):
      self.sdr.setSampleRate(SOAPY_SDR_RX, RX1, fs)          # Set sample rate
      self.sdr.setGainMode(SOAPY_SDR_RX, RX1, True)       # Set the gain mode
      self.sdr.setGain(SOAPY_SDR_RX, RX1, "TIA", 0)
      self.sdr.setGain(SOAPY_SDR_RX, RX1, "LNA", 0)
      self.sdr.setGain(SOAPY_SDR_RX, RX1, "PGA", 0) # programmable-gain amplifier (PGA)
      self.sdr.setFrequency(SOAPY_SDR_RX, RX1, self.freq)         # Tune the LO    
      self.RX1_buff = np.empty(2 * self.N, np.int16)                 # Create memory buffer for data stream
      self.sdr.setBandwidth(SOAPY_SDR_RX, RX1, rx_bw)
      self.sdr.setAntenna(SOAPY_SDR_RX, RX1, "LNAL")
      self.rx_stream = self.sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16, [RX1])  # Setup data stream
     
   
    elif(self.channel[0] == 2):
      self.sdr.setSampleRate(SOAPY_SDR_RX, RX2, fs)          # Set sample rate
      self.sdr.setGainMode(SOAPY_SDR_RX, RX2, True)       # Set the gain mode
      self.sdr.setGain(SOAPY_SDR_RX, RX2, "TIA", 0)
      self.sdr.setGain(SOAPY_SDR_RX, RX2, "LNA", 0)
      self.sdr.setGain(SOAPY_SDR_RX, RX2, "PGA", 0) # programmable-gain amplifier (PGA)
      self.sdr.setFrequency(SOAPY_SDR_RX, RX2, self.freq)         # Tune the LO    
      self.RX2_buff = np.empty(2 * self.N, np.int16)                 # Create memory buffer for data stream
      self.sdr.setBandwidth(SOAPY_SDR_RX, RX2, rx_bw)
      self.sdr.setAntenna(SOAPY_SDR_RX, RX2, "LNAL")
      self.rx_stream = self.sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16, [RX2])  # Setup data stream
   
    else:
      print("Channel amount has to be 1 or 2")

  #this function reads stream of data and puts it in self.rx_stream numpy array   
  def get_signal(self):
    #  Initialize the AIR-T receiver using SoapyAIRT
    self.sdr.activateStream(self.rx_stream)  # this turns the radio on
    time.sleep(0.8)
     # Read the samples from the data buffer
    if (len(self.channel) == 2):
      sr = self.sdr.readStream(self.rx_stream, [self.RX1_buff, self.RX2_buff], self.N, timeoutUs = self.timeout_us)
    elif(self.channel[0] == 1):
      sr = self.sdr.readStream(self.rx_stream, [self.RX1_buff], self.N, timeoutUs = self.timeout_us)    
    elif(self.channel[0] == 2):
      sr = self.sdr.readStream(self.rx_stream, [self.RX2_buff], self.N, timeoutUs = self.timeout_us)
  
    rc = sr.ret # number of samples read or the error code
    assert rc == self.N, 'Error Reading Samples from Device (error code = %d)!' % rc
    # Stop streaming
    self.sdr.deactivateStream(self.rx_stream)
    self.sdr.closeStream(self.rx_stream)
    
  #this function makes complex64 from ADC bits and saves it as binary file  
  def make_iq(self, filenames):
    if (len(self.channel) == 2):
    # Convert interleaved shorts (received signal) to numpy.complex64 normalized between [-1, 1]
      RX1bits = self.RX1_buff.astype(float) / np.power(2.0, self.rx_bits-1)
      RX2bits = self.RX2_buff.astype(float) / np.power(2.0, self.rx_bits-1)
      RX1complex = (RX1bits[::2] + 1j*RX1bits[1::2]).astype(np.complex64) 
      RX2complex = (RX2bits[::2] + 1j*RX2bits[1::2]).astype(np.complex64)
      RX1complex = np.complex64(RX1complex)
      RX2complex = np.complex64(RX2complex)
      RX1complex = np.insert(RX1complex, 0, (self.N + 1j*self.freq) )
      RX2complex = np.insert(RX2complex, 0, (self.N + 1j*self.freq) )
      RX1complex.tofile(filenames[0])
      RX2complex.tofile(filenames[1])
   
    elif(self.channel[0] == 1):
      RX1bits = self.RX1_buff.astype(float) / np.power(2.0, self.rx_bits-1)
      RX1complex = (RX1bits[::2] + 1j*RX1bits[1::2]) 
      RX1complex = np.insert(RX1complex, 0, (self.N + 1j*self.freq) )
      RX1complex = np.complex64(RX1complex)
      RX1complex.tofile(filenames[0])
   
    elif(self.channel[0] == 2):
      RX2bits = self.RX2_buff.astype(float) / np.power(2.0, self.rx_bits-1)
      RX2complex = (RX2bits[::2] + 1j*RX2bits[1::2]) 
      RX2complex = np.insert(RX2complex, 0, (self.N + 1j*self.freq) )
      RX2complex = np.complex64(RX2complex)
      RX2complex.tofile(filenames[0])

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--center", type=float, nargs='?', help="Set local oscillator frequency")
  parser.add_argument("--time", type=int, nargs='?', help="Set measurement time")
  parser.add_argument("--samprate", type=float, nargs='?', help="Set sampling rate")
  parser.add_argument("--bw", type=float, nargs='?', help="Set bandwidth")
  parser.add_argument("--channel", type=int, nargs='+', help="Set channels to read data from")
  parser.add_argument("--filename", type=str, action='append', nargs='+', help="Path to saved file")
  args = parser.parse_args()
  
  if args.time and args.samprate and args.bw and args.filename and args.channel:
    print ("Central frequency set to ", args.center, " Hz.")
    print ("Measurement time set to ", args.time, " sec.")
    print ("Sampling rate set to ", args.samprate, " Samples/sec.")
    print ("Bandwidth set to ", args.bw, " Hz.")

    if ( len(args.channel) == len(args.filename[0]) and len(args.channel) == 1 ):
      print ("Reading from channels ", args.channel[0])
      print ("file saved as: ", args.filename[0][0])
      #initialize Lime SDR with entered measure time, bandwidth, sampling rate
      Lime = LimeSDR(args.center, args.time, args.bw, args.samprate, args.channel)
      Lime.get_signal()
      Lime.make_iq(args.filename[0])
    
    elif ( len(args.channel) == len(args.filename[0]) and len(args.channel) == 2 ):
      print ("Reading from channels ", args.channel[0],args.channel[1])
      print ("file saved as: ", args.filename[0][0], args.filename[0][1])
      #initialize Lime SDR with entered measure time, bandwidth, sampling rate
      Lime = LimeSDR(args.center, args.time, args.bw, args.samprate, args.channel)
      Lime.get_signal()
      Lime.make_iq(args.filename[0])
    
    else:
      print ("channels amount not equal to amount of files")     
  else:
    print ("No parameters were given")

