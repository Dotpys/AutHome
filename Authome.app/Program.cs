using Microsoft.AspNetCore.ResponseCompression;
using AutHome.Data;
using AutHome.Hubs;
using AutHome.Workers;
using AutHome;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddResponseCompression(opts =>
{
    opts.MimeTypes = ResponseCompressionDefaults.MimeTypes.Concat(
        new[] { "application/octet-stream" });
});
builder.Services.AddHostedService<AutHomeConnectionService>();
builder.Services.AddDbContext<AutHomeContext>();

var app = builder.Build();

// Configure the HTTP request pipeline.
app.UseResponseCompression();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();

app.UseStaticFiles();

app.UseRouting();

app.MapBlazorHub();
app.MapHub<ControlHub>("/controlhub");
app.MapFallbackToPage("/_Host");

app.Run();
