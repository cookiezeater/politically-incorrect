package com.sacs.shao.friendsagainsthumanity;

import android.util.Log;

import com.loopj.android.http.*;

import org.apache.http.entity.StringEntity;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;


public class FriendlyConsumer {
    private static final String TAG = FriendlyConsumer.class.getName();
    private static final String BASE_URL = "http://damp-wildwood-9070.herokuapp.com";
    private static AsyncHttpClient client = new AsyncHttpClient();

    private static void get(
            String url, RequestParams params, AsyncHttpResponseHandler responseHandler) {
        client.get(getAbsoluteUrl(url), params, responseHandler);
    }

    private static void post(
            String url, StringEntity entity, AsyncHttpResponseHandler responseHandler) {
        client.post(null, getAbsoluteUrl(url), entity, "application/json", responseHandler);
    }

    private static String getAbsoluteUrl(String relativeUrl) {
        return BASE_URL + relativeUrl;
    }

    public static void createPlayer(String username, String password,
                                    String email, String firstName,
                                    String lastName, AsyncHttpResponseHandler responseHandler)
            throws JSONException, UnsupportedEncodingException {
        JSONObject playerInfo = new JSONObject();
        playerInfo.put("username", username);
        playerInfo.put("password", password);
        playerInfo.put("email", email);
        playerInfo.put("first_name", firstName);
        playerInfo.put("last_name", lastName);

        StringEntity playerInfoString = new StringEntity(playerInfo.toString());

        Log.d(TAG, playerInfo.toString());

        post("/players", playerInfoString, responseHandler);
    }
}
