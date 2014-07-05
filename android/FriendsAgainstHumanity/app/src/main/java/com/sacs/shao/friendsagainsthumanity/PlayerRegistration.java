package com.sacs.shao.friendsagainsthumanity;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import com.loopj.android.http.JsonHttpResponseHandler;

import org.apache.http.Header;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;


public class PlayerRegistration extends Activity {
    private static final String TAG = PlayerRegistration.class.getName();
    private Context context;
    private SharedPreferences preferences;
    private Intent intent;
    private EditText usernameField;
    private EditText passwordField;
    private EditText emailField;
    private EditText firstNameField;
    private EditText lastNameField;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_player_registration);

        context = getApplicationContext();

        preferences = this.getSharedPreferences(
                "com.sacs.shao.friendsagainsthumanity", Context.MODE_PRIVATE);

        if (preferences.getInt("playerID", 0) != 0) {
            intent = new Intent(this, MainGame.class);
            startActivity(intent);
        }

        usernameField = (EditText) findViewById(R.id.username);
        passwordField = (EditText) findViewById(R.id.password);
        emailField = (EditText) findViewById(R.id.email);
        firstNameField = (EditText) findViewById(R.id.firstName);
        lastNameField = (EditText) findViewById(R.id.lastName);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.apitester, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();
        if (id == R.id.action_settings) {
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    public void playerRegistrationButton(View view) {
        String username = usernameField.getText().toString();
        String password = passwordField.getText().toString();
        String email = emailField.getText().toString();
        String firstName = firstNameField.getText().toString();
        String lastName = lastNameField.getText().toString();

        playerRegister(username, password, email, firstName, lastName);
    }

    public void playerRegister(String username, String password,
                               String email, String firstName,
                               String lastName) {
        try {
            FriendlyConsumer.createPlayer(username, password, email, firstName, lastName,
                    new JsonHttpResponseHandler() {

                        @Override
                        public void onSuccess(int statusCode,
                                              Header[] headers,
                                              JSONObject response) {
                            String responseStatus;
                            int playerID = -1;

                            try {
                                responseStatus = response.getString("status");
                            } catch (JSONException e) {
                                responseStatus = "failure";
                            }

                            if (responseStatus.equals("success")) {
                                try {
                                    playerID = response.getInt("player_id");
                                } catch (JSONException e) {
                                    Log.d(TAG, "SHIT");
                                }
                            } else if (responseStatus.equals("failure")) {
                                String message;

                                try {
                                    message = response.getString("message");
                                } catch (JSONException e) {
                                    message = "Shit...";
                                }

                                Log.d(TAG, message);
                            }

                            preferences.edit().putInt("playerID", playerID).commit();
                            Log.d(TAG, Integer.toString(preferences.getInt("playerID", playerID)));
                        }

                        @Override
                        public void onFailure(int statusCode,
                                              Header[] headers,
                                              String responseString,
                                              Throwable throwable) {
                            String message = "Something went terribly wrong...";
                            int duration = Toast.LENGTH_SHORT;
                            Toast toast = Toast.makeText(context, message, duration);
                            toast.show();
                        }

                        // launch game activity
                    }
            );
        } catch (JSONException e) {
            e.printStackTrace();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
    }
}
