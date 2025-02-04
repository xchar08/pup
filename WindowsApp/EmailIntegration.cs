using System.Collections.Generic;
using System.Threading.Tasks;

namespace ShibaInuAssistant
{
    public static class EmailIntegration
    {
        // Stub method for sending an email via Outlook (Microsoft Graph).
        public static async Task<bool> SendEmailAsync(string to, string subject, string body)
        {
            await Task.Delay(1000);
            // In production, integrate with Microsoft Graph API using the Outlook credentials from appsettings.json.
            return true;
        }

        // Stub method for fetching emails.
        public static async Task<List<string>> FetchEmailsAsync()
        {
            await Task.Delay(1000);
            return new List<string>
            {
                "Email 1: Meeting Reminder",
                "Email 2: Project Update",
                "Email 3: Newsletter"
            };
        }
    }
}
