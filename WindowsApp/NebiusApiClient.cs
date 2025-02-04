using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace ShibaInuAssistant
{
    public class NebiusApiClient
    {
        private static readonly HttpClient _client = new HttpClient();
        private readonly string _apiUrl;
        private readonly string _apiKey;

        public NebiusApiClient(string apiUrl, string apiKey)
        {
            _apiUrl = apiUrl;
            _apiKey = apiKey;
            _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", _apiKey);
        }

        public async Task<CompletionResponse?> CreateCompletionAsync(string model, string prompt, int maxTokens = 100, double temperature = 1.0, double topP = 1.0)
        {
            var requestBody = new
            {
                model = model,
                prompt = prompt,
                max_tokens = maxTokens,
                temperature = temperature,
                top_p = topP
            };

            string jsonBody = JsonSerializer.Serialize(requestBody);
            var content = new StringContent(jsonBody, Encoding.UTF8, "application/json");

            var response = await _client.PostAsync(_apiUrl, content);
            response.EnsureSuccessStatusCode();
            string responseJson = await response.Content.ReadAsStringAsync();
            var completionResponse = JsonSerializer.Deserialize<CompletionResponse>(
                responseJson,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
            );
            return completionResponse;
        }
    }

    public class CompletionResponse
    {
        public string? id { get; set; }
        public string? @object { get; set; }
        public int created { get; set; }
        public string? model { get; set; }
        public CompletionChoice[]? choices { get; set; }
        public Usage? usage { get; set; }
    }

    public class CompletionChoice
    {
        public string? text { get; set; }
        public int index { get; set; }
        public string? finish_reason { get; set; }
    }

    public class Usage
    {
        public int prompt_tokens { get; set; }
        public int completion_tokens { get; set; }
        public int total_tokens { get; set; }
    }
}
