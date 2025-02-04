using System.IO;
using System.Windows;
using Microsoft.Extensions.Configuration;

namespace ShibaInuAssistant
{
    public partial class App : Application
    {
        public static IConfigurationRoot? Configuration { get; private set; }

        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // TEMPORARY DEBUG: Confirm application startup
            MessageBox.Show("Application Starting", "Debug");

            var builder = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
                .AddEnvironmentVariables();

            Configuration = builder.Build();
        }
    }
}
