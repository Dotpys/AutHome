using Microsoft.AspNetCore.ResponseCompression;
using AutHome.Data;
using AutHome.Hubs;
using AutHome.Services;
using AutHome;
using Microsoft.Extensions.FileProviders;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddResponseCompression(opts =>
{
	opts.MimeTypes = ResponseCompressionDefaults.MimeTypes.Concat(
		new[] { "application/octet-stream" });
});
builder.Services.AddDbContext<AuthomeContext>();
builder.Services.AddSingleton<FingerprintImageStore>();
builder.Services.AddHostedService<MQTTConnectionService>();
builder.Services.AddSingleton<UserFingerprintService>();


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
app.UseStaticFiles(new StaticFileOptions
{
	FileProvider = new PhysicalFileProvider(
		   Path.Combine(builder.Environment.ContentRootPath, "Finger")),
	RequestPath = "/cdn/image"
});

app.UseRouting();

app.MapBlazorHub();
app.MapHub<DashboardHub>("/hub/dashboard");
app.MapHub<UsersHub>("/hub/users");
app.MapFallbackToPage("/_Host");

app.Run();
