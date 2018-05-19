package testSocket;

public class conditioner {

    private int type;           //请求报文类型
    private int room;           //房号
    private int _switch;        //开关
    private float temperature;  //温度
    private int wind;           //风速

    public conditioner(float temperature, int wind, int room, int _switch) {
        this.temperature = temperature;
        this.wind = wind;
        this.room = room;
        this._switch = _switch;
    }
    //无参构造
    conditioner() {
    }

    public int getType() {
        return type;
    }

    public void setType(int type) {
        this.type = type;
    }

    public float getTemperature() {
        return temperature;
    }

    public void setTemperature(float temperature) {
        this.temperature = temperature;
    }

    public int getWind() {
        return wind;
    }

    public void setWind(int wind) {
        this.wind = wind;
    }

    public int getRoom() {
        return room;
    }

    public void setRoom(int room) {
        this.room = room;
    }

    public int get_switch() {
        return _switch;
    }

    public void set_switch(int _switch) {
        this._switch = _switch;
    }
}
