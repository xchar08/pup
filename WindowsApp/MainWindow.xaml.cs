using System;
using System.Threading.Tasks;
using System.Windows;

namespace ShibaInuAssistant
{
    public partial class MainWindow : Window
    {
        private readonly string _nebiusEndpoint;
        private readonly string _nebiusApiKey;
        private readonly string _nebiusModelId;

        public MainWindow()
        {
            InitializeComponent();
            this.Closed += MainWindow_Closed;

            // Retrieve Nebius API settings from appsettings.json
            _nebiusEndpoint = App.Configuration?["NebiusApi:Endpoint"] ?? "";
            _nebiusApiKey = App.Configuration?["NebiusApi:ApiKey"] ?? "";
            _nebiusModelId = App.Configuration?["NebiusApi:ModelId"] ?? "";
        }

        private void MainWindow_Closed(object? sender, EventArgs e)
        {
            // When the main window closes, show the widget again.
            var widget = new WidgetWindow();
            widget.Show();
        }

        private async void GetCompletionButton_Click(object sender, RoutedEventArgs e)
        {
            string prompt = PromptTextBox.Text;
            if (string.IsNullOrWhiteSpace(prompt))
            {
                MessageBox.Show("Please enter a prompt.");
                return;
            }

            try
            {
                var client = new NebiusApiClient(_nebiusEndpoint, _nebiusApiKey);
                var response = await client.CreateCompletionAsync(_nebiusModelId, prompt);
                if (response != null && response.choices != null && response.choices.Length > 0)
                {
                    CompletionTextBox.Text = response.choices[0].text;
                }
                else
                {
                    CompletionTextBox.Text = "No completion returned.";
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

        private async void StartTranslationButton_Click(object sender, RoutedEventArgs e)
        {
            string textToTranslate = PromptTextBox.Text;
            if (string.IsNullOrWhiteSpace(textToTranslate))
            {
                MessageBox.Show("Enter text to translate in the Assistant tab.");
                return;
            }
            try
            {
                // Simulate translation.
                string translated = await Task.Run(() => textToTranslate + " [Translated]");
                TranslationTextBox.Text = translated;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Translation error: {ex.Message}");
            }
        }
    }
}
