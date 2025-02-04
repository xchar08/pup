using System;
using System.Diagnostics;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media.Animation;
using NAudio.Wave;
using Vosk;

namespace ShibaInuAssistant
{
    public partial class WidgetWindow : Window
    {
        private Model? voskModel;
        private WaveInEvent? waveIn;
        private VoskRecognizer? recognizer;
        private const int sampleRate = 16000;

        public WidgetWindow()
        {
            InitializeComponent();
            Loaded += WidgetWindow_Loaded;
            InitializeVoskAsync();
        }

        private void WidgetWindow_Loaded(object sender, RoutedEventArgs e)
        {
            // TEMPORARY DEBUG: Confirm that the widget window has loaded.
            MessageBox.Show("WidgetWindow Loaded", "Debug");

            // Position the widget at the bottom-right with a 20-pixel margin.
            var workArea = SystemParameters.WorkArea;
            Left = workArea.Right - Width - 20;
            Top = workArea.Bottom - Height - 20;
        }

        private async void InitializeVoskAsync()
        {
            try
            {
                // Set Vosk logging level to 0 (no logging) to reduce native output and potential issues.
                Vosk.Vosk.SetLogLevel(0);

                // Initialize Vosk model. Ensure the path matches your extracted model folder.
                voskModel = new Model("Models/vosk-model-small-en-us-0.15");
                recognizer = new VoskRecognizer(voskModel, sampleRate);

                // Set up NAudio to capture audio from the default microphone.
                waveIn = new WaveInEvent
                {
                    DeviceNumber = 0,
                    WaveFormat = new WaveFormat(sampleRate, 1)
                };
                waveIn.DataAvailable += WaveIn_DataAvailable;
                waveIn.RecordingStopped += WaveIn_RecordingStopped;
                waveIn.StartRecording();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Vosk initialization failed: " + ex.Message, "Error");
            }
            await Task.CompletedTask; // To satisfy the async method signature.
        }

        private void WaveIn_DataAvailable(object? sender, WaveInEventArgs e)
        {
            try
            {
                if (recognizer != null && recognizer.AcceptWaveform(e.Buffer, e.BytesRecorded))
                {
                    var resultJson = recognizer.Result();
                    ProcessVoskResult(resultJson);
                }
                else if (recognizer != null)
                {
                    // Optionally, process partial results:
                    var partialResultJson = recognizer.PartialResult();
                    // You can log or display partial results if desired.
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine("Error in audio processing: " + ex.Message);
            }
        }

        private void WaveIn_RecordingStopped(object? sender, StoppedEventArgs e)
        {
            // Optional: handle recording stopped event.
        }

        private void ProcessVoskResult(string resultJson)
        {
            try
            {
                using var doc = JsonDocument.Parse(resultJson);
                if (doc.RootElement.TryGetProperty("text", out JsonElement textElement))
                {
                    string recognizedText = textElement.GetString()?.ToLower() ?? "";
                    if (!string.IsNullOrWhiteSpace(recognizedText))
                    {
                        Dispatcher.Invoke(() =>
                        {
                            if (recognizedText.StartsWith("open ") || recognizedText.StartsWith("close "))
                            {
                                ProcessAppCommand(recognizedText);
                            }
                            else
                            {
                                StartPurpleWaveAnimation(recognizedText);
                            }
                        });
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine("Error processing Vosk result: " + ex.Message);
            }
        }

        private void StartPurpleWaveAnimation(string recognizedText)
        {
            PurpleWaveCanvas.Opacity = 0;
            var animation = new DoubleAnimation
            {
                From = 0,
                To = 1,
                Duration = TimeSpan.FromMilliseconds(200),
                AutoReverse = true
            };
            PurpleWaveCanvas.BeginAnimation(OpacityProperty, animation);
            ToolTip = recognizedText;
        }

        private void ProcessAppCommand(string command)
        {
            try
            {
                if (command.StartsWith("open "))
                {
                    string appName = command.Substring("open ".Length).Trim();
                    Process.Start(new ProcessStartInfo(appName + ".exe") { UseShellExecute = true });
                }
                else if (command.StartsWith("close "))
                {
                    string appName = command.Substring("close ".Length).Trim();
                    var processes = Process.GetProcessesByName(appName);
                    foreach (var proc in processes)
                    {
                        proc.Kill();
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error processing command: " + ex.Message, "Command Error");
            }
        }

        protected override void OnMouseLeftButtonDown(MouseButtonEventArgs e)
        {
            base.OnMouseLeftButtonDown(e);
            // Open the full assistant window and stop audio capture.
            var mainWindow = new MainWindow();
            mainWindow.Show();
            StopAudioCapture();
            Hide();
        }

        private void StopAudioCapture()
        {
            if (waveIn != null)
            {
                waveIn.StopRecording();
                waveIn.Dispose();
                waveIn = null;
            }
            recognizer?.Dispose();
            voskModel?.Dispose();
        }

        protected override void OnClosed(EventArgs e)
        {
            StopAudioCapture();
            base.OnClosed(e);
        }
    }
}
