using AutHome.Data;

using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;

namespace AutHome.Services;

public class FingerprintImageStore
{
	private const int IMAGE_WIDTH = 256;
	private const int IMAGE_HEIGHT = 288;
	private const int INPUT_BUFFER_SIZE = (IMAGE_WIDTH * IMAGE_HEIGHT)/2;

	private readonly AuthomeContext _authomeContext;

	public FingerprintImageStore()
	{
		_authomeContext = new AuthomeContext();
	}

	~FingerprintImageStore()
	{
		_authomeContext.Dispose();
	}

	public bool TryEncodeAndSaveAsImage(byte[] data, out FingerImage? result)
	{
		//Input data check
		if (data == null || data.Length != INPUT_BUFFER_SIZE)
		{
			result = null;
			return false;
		}
		//Image decompression
		L8[] encodedData = new L8[IMAGE_WIDTH * IMAGE_HEIGHT];
		for (int i=0; i< INPUT_BUFFER_SIZE; i++)
		{
			encodedData[i * 2 + 0] = new L8((byte)((data[i] & 0xF0) << 0));
			encodedData[i * 2 + 1] = new L8((byte)((data[i] & 0x0F) << 4));
		}
		//Image creation
		Image<L8> image = Image.LoadPixelData(encodedData, IMAGE_WIDTH, IMAGE_HEIGHT);
		//Database entry cration
		result = new FingerImage()
		{
			Id = Guid.NewGuid(),
			Timestamp = DateTime.UtcNow
		};
		_authomeContext.Images.Add(result);
		//Saves the image on the file system
		image.SaveAsPng($"Finger/{result.Id:N}.png");
		//Saves the database
		_authomeContext.SaveChanges();
		return true;
	}
}
