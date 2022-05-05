namespace AutHome.Data;

public class AreaOfInterest
{
	public string Name { get; set; } = string.Empty;
	public string Description { get; set; } = string.Empty;
	public ICollection<ISensor> Sensors { get; set; }
	public ICollection<IActuator> Actuators { get; set; }
}